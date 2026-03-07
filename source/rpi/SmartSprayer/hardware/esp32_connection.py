# esp32_connection.py
# USB serial connection manager for ESP32 controller.
#
# Responsibilities:
#   - Scan available USB serial ports (/dev/ttyUSB*, /dev/ttyACM* on Linux; COM* on Windows)
#   - Connect / disconnect with automatic fallback across available ports
#   - Persist the last successful port to data/usb_config.json
#   - Background auto-reconnect loop (non-blocking)
#   - Emit status callbacks so UI can react without polling
#
# Configurable class-level constants (can be overridden before instantiation):
#   ESP32Connection.USB_SCAN_INTERVAL      -- seconds between reconnect probes  (default 5)
#   ESP32Connection.AUTO_RECONNECT_ENABLED -- enable/disable auto-reconnect     (default True)
#   ESP32Connection.LAST_CONNECTED_PORT    -- seed port (overridden at runtime)  (default None)

import glob
import json
import os
import sys
import threading
import time

import serial
import serial.tools.list_ports

# ── paths ─────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "..", "data")
_CONFIG_FILE = os.path.join(_DATA_DIR, "usb_config.json")

# ── connection states ─────────────────────────────────────────────────────────
STATE_DISCONNECTED = "Disconnected"
STATE_CONNECTED    = "Connected"
STATE_ERROR        = "Error"
STATE_CONNECTING   = "Connecting…"


class ESP32Connection:
    """Manages the USB serial link to the ESP32 controller.

    Usage
    -----
        conn = ESP32Connection(baudrate=9600, on_status_change=my_callback)
        conn.start()                    # begins auto-connect + monitor loop
        conn.connect("/dev/ttyUSB0")    # manual override
        conn.disconnect()
        conn.stop()                     # clean shutdown

    Callbacks
    ---------
        on_status_change(state: str, port: str | None, message: str)
            Called from a daemon thread whenever the connection state changes.
            Schedule UI updates with widget.after(0, ...) in the callback.
    """

    # ── configurable defaults ──────────────────────────────────────────────
    USB_SCAN_INTERVAL:      float = 5.0   # seconds between reconnect probes
    AUTO_RECONNECT_ENABLED: bool  = True
    LAST_CONNECTED_PORT:    str | None = None

    # On Linux only these three ttyUSB ports are considered for ESP32.
    # Set to None to allow all detected ports.
    ALLOWED_PORTS: list[str] | None = [
        "/dev/ttyUSB0",
        "/dev/ttyUSB1",
        "/dev/ttyUSB2",
    ]

    # ── serial parameters ──────────────────────────────────────────────────
    DEFAULT_BAUDRATE: int = 9600
    DEFAULT_TIMEOUT:  float = 1.0

    def __init__(
        self,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        on_status_change=None,
        on_log=None,
        debug: bool = False,
    ):
        self.baudrate = baudrate
        self.timeout  = timeout
        self.debug    = debug

        # callbacks
        self._on_status_change = on_status_change  # (state, port, message)
        self._on_log           = on_log             # (message)

        # runtime state
        self.serial_connection: serial.Serial | None = None
        self.state   = STATE_DISCONNECTED
        self.port    = None          # currently connected port
        self._lock   = threading.Lock()
        self._stop_event = threading.Event()
        self._monitor_thread: threading.Thread | None = None

        # load last-used port from disk
        self.LAST_CONNECTED_PORT = self._load_last_port()

    # ══════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════════════

    def start(self):
        """Start background auto-connect/monitor loop."""
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="ESP32-Monitor"
        )
        self._monitor_thread.start()

    def stop(self):
        """Stop background loop and close connection cleanly."""
        self._stop_event.set()
        self.disconnect()

    def connect(self, port: str) -> bool:
        """Attempt to connect to a specific port.

        Returns True on success.  Thread-safe.
        """
        with self._lock:
            return self._connect_port(port)

    def disconnect(self):
        """Close the current serial connection.  Thread-safe."""
        with self._lock:
            self._close_serial()
            self._set_state(STATE_DISCONNECTED, None, "Disconnected by user.")

    def reconnect(self) -> bool:
        """Try to reconnect: last-known port first, then scan.  Thread-safe."""
        with self._lock:
            return self._auto_connect()

    @property
    def is_connected(self) -> bool:
        return self.state == STATE_CONNECTED and self.serial_connection is not None

    def scan_ports(self) -> list[str]:
        """Return a sorted list of available USB serial port names."""
        return _list_serial_ports(self.ALLOWED_PORTS)

    def write(self, data: bytes) -> bool:
        """Non-blocking write.  Returns False if not connected."""
        if not self.is_connected:
            return False
        try:
            with self._lock:
                if self.serial_connection:
                    self.serial_connection.write(data)
            return True
        except serial.SerialException as exc:
            self._log(f"[write error] {exc}")
            self._handle_disconnect(str(exc))
            return False

    def readline(self) -> str | None:
        """Non-blocking readline.  Returns decoded string or None."""
        if not self.is_connected:
            return None
        try:
            with self._lock:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    raw = self.serial_connection.readline()
                    return raw.decode("utf-8", errors="ignore").strip()
        except serial.SerialException as exc:
            self._log(f"[read error] {exc}")
            self._handle_disconnect(str(exc))
        return None

    def bytes_waiting(self) -> int:
        """Return number of bytes in the receive buffer (0 if disconnected)."""
        try:
            if self.serial_connection and self.is_connected:
                return self.serial_connection.in_waiting
        except Exception:
            pass
        return 0

    # ══════════════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════════════════

    def _load_last_port(self) -> str | None:
        try:
            if os.path.exists(_CONFIG_FILE):
                with open(_CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
                return cfg.get("last_port") or None
        except Exception as exc:
            self._log(f"[config] Failed to load usb_config.json: {exc}")
        return None

    def _save_last_port(self, port: str):
        try:
            os.makedirs(_DATA_DIR, exist_ok=True)
            cfg = {}
            if os.path.exists(_CONFIG_FILE):
                try:
                    with open(_CONFIG_FILE, "r") as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
            cfg["last_port"] = port
            cfg["auto_reconnect"] = self.AUTO_RECONNECT_ENABLED
            cfg["scan_interval"] = self.USB_SCAN_INTERVAL
            with open(_CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception as exc:
            self._log(f"[config] Failed to save usb_config.json: {exc}")

    # ══════════════════════════════════════════════════════════════════════
    # INTERNAL — connection helpers
    # ══════════════════════════════════════════════════════════════════════

    def _connect_port(self, port: str) -> bool:
        """Internal connect — must be called with self._lock held."""
        self._close_serial()
        self._set_state(STATE_CONNECTING, port, f"Connecting to {port}…")
        try:
            self.serial_connection = serial.Serial(
                port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            time.sleep(2)   # wait for ESP32 reset after DTR toggle
            # Verify the port opened successfully
            if not self.serial_connection.is_open:
                raise serial.SerialException("Port did not open.")
            self.port = port
            self.LAST_CONNECTED_PORT = port
            self._save_last_port(port)
            self._set_state(STATE_CONNECTED, port, f"Connected to {port}.")
            self._log(f"[ESP32] Connected on {port}")
            return True
        except serial.SerialException as exc:
            self._close_serial()
            msg = _friendly_serial_error(str(exc))
            self._set_state(STATE_ERROR, port, msg)
            self._log(f"[ESP32] {msg}")
            return False
        except Exception as exc:
            self._close_serial()
            self._set_state(STATE_ERROR, port, str(exc))
            self._log(f"[ESP32] Unexpected error on {port}: {exc}")
            return False

    def _close_serial(self):
        """Close serial without changing state."""
        try:
            if self.serial_connection:
                self.serial_connection.close()
        except Exception:
            pass
        finally:
            self.serial_connection = None

    def _auto_connect(self) -> bool:
        """Try last-known port; on failure try all available ports."""
        candidates = _list_serial_ports(self.ALLOWED_PORTS)

        # Put last-known port at front of the list
        if self.LAST_CONNECTED_PORT:
            candidates = _prioritise(self.LAST_CONNECTED_PORT, candidates)

        if not candidates:
            self._set_state(STATE_DISCONNECTED, None, "No USB serial devices found.")
            self._log("[ESP32] No USB serial devices found.")
            return False

        for port in candidates:
            self._log(f"[ESP32] Trying {port}…")
            if self._connect_port(port):
                return True
            time.sleep(0.5)

        self._set_state(STATE_ERROR, None, "All ports tried — ESP32 not found.")
        return False

    def _handle_disconnect(self, reason: str = ""):
        """Called when an active connection drops unexpectedly."""
        self._close_serial()
        self._set_state(STATE_ERROR, self.port, f"Connection lost: {reason}")
        self._log(f"[ESP32] Connection lost on {self.port}: {reason}")
        self.port = None

    # ══════════════════════════════════════════════════════════════════════
    # BACKGROUND MONITOR
    # ══════════════════════════════════════════════════════════════════════

    def _monitor_loop(self):
        """Daemon thread: initial connect then periodic health-check + reconnect."""
        # Initial auto-connect attempt
        with self._lock:
            self._auto_connect()

        while not self._stop_event.is_set():
            time.sleep(self.USB_SCAN_INTERVAL)
            if self._stop_event.is_set():
                break

            if not self.AUTO_RECONNECT_ENABLED:
                continue

            # Health-check: try an in_waiting probe (lightweight)
            alive = False
            try:
                with self._lock:
                    if self.serial_connection and self.serial_connection.is_open:
                        _ = self.serial_connection.in_waiting   # raises if unplugged
                        alive = True
            except Exception as exc:
                self._handle_disconnect(str(exc))

            if not alive and not self._stop_event.is_set():
                self._log("[ESP32] Attempting auto-reconnect…")
                with self._lock:
                    self._auto_connect()

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _set_state(self, state: str, port, message: str):
        self.state = state
        self.port  = port if state == STATE_CONNECTED else self.port
        if self._on_status_change:
            try:
                self._on_status_change(state, port, message)
            except Exception as exc:
                print(f"[ESP32Connection] status callback error: {exc}")

    def _log(self, message: str):
        print(message)
        if self._on_log:
            try:
                self._on_log(message)
            except Exception:
                pass
        if self.debug:
            print(f"[DEBUG] {message}")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _list_serial_ports(allowed: "list[str] | None" = None) -> list[str]:
    """Return sorted list of USB serial port names on the current platform.

    Parameters
    ----------
    allowed:
        When provided, only return ports whose device name is in this list.
        On Linux the default class constant restricts scanning to
        /dev/ttyUSB0, /dev/ttyUSB1, /dev/ttyUSB2.
        Pass None to return all detected ports.
    """
    ports = []

    if sys.platform.startswith("linux"):
        # On Linux use only the explicitly allowed ttyUSB ports (if set)
        candidates = allowed if allowed is not None else [
            f"/dev/ttyUSB{i}" for i in range(10)
        ]
        for p in candidates:
            if glob.glob(p):          # exists in /dev
                if p not in ports:
                    ports.append(p)
    else:
        # Windows / macOS: use pyserial enumerator
        for p in serial.tools.list_ports.comports():
            ports.append(p.device)

    # Deduplicate and sort (ttyUSB0 < ttyUSB1 < ttyUSB2 etc.)
    return sorted(set(ports))


def _prioritise(preferred: str, candidates: list[str]) -> list[str]:
    """Return candidates with preferred at index 0 (if present)."""
    rest = [p for p in candidates if p != preferred]
    return [preferred] + rest if preferred else rest


def _friendly_serial_error(msg: str) -> str:
    """Convert pyserial error text to a user-friendly message."""
    m = msg.lower()
    if "permission denied" in m:
        return f"Permission denied. Run: sudo usermod -aG dialout $USER"
    if "no such file" in m or "could not open port" in m:
        return "Port not found — ESP32 may be unplugged."
    if "device or resource busy" in m:
        return "Port is busy — another app may be using it."
    return msg[:120]
