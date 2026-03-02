# keyboard_utils.py
# Onboard virtual keyboard auto-show/hide helpers for SmartSprayerV2
#
# Usage in any screen/panel:
#
#   from ui.keyboard_utils import bind_keyboard, show_keyboard, hide_keyboard
#
#   bind_keyboard(self.phone_entry)   # auto-show on focus, hide on focus-out
#   bind_keyboard(self.passw)
#
# Note: works on Raspberry Pi with Onboard installed.
# On non-RPi systems (dev machines) the functions silently do nothing.

import subprocess
import sys

# ── platform guard ────────────────────────────────────────────────────────────
# Only attempt to launch Onboard on Linux (Raspberry Pi).
_IS_LINUX = sys.platform.startswith("linux")

_onboard_proc: "subprocess.Popen | None" = None


def show_keyboard():
    """
    Launch the Onboard virtual keyboard if it is not already running.
    Uses a compact Phone layout suitable for a touchscreen.
    Called automatically by bind_keyboard() on <FocusIn>.
    """
    if not _IS_LINUX:
        return

    global _onboard_proc
    try:
        # If already running, do nothing
        if _onboard_proc is not None and _onboard_proc.poll() is None:
            return
        _onboard_proc = subprocess.Popen(
            [
                "onboard",
                "--size=800x280",
                "--layout=Phone",
                "--theme=Nightshade",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("[keyboard_utils] Onboard not found — install with: sudo apt install onboard")
    except Exception as e:
        print(f"[keyboard_utils] Could not launch Onboard: {e}")


def hide_keyboard():
    """
    Terminate the Onboard virtual keyboard.
    Called automatically by bind_keyboard() on <FocusOut>.
    Also call this explicitly before destroying a window/screen.
    """
    if not _IS_LINUX:
        return

    global _onboard_proc
    try:
        if _onboard_proc is not None and _onboard_proc.poll() is None:
            _onboard_proc.terminate()
    except Exception as e:
        print(f"[keyboard_utils] Could not terminate Onboard: {e}")
    finally:
        _onboard_proc = None


def bind_keyboard(widget):
    """
    Attach Onboard show/hide bindings to a CTkEntry (or any Tkinter widget).

    - Shows Onboard when the widget receives focus (<FocusIn>).
    - Hides Onboard when the widget loses focus (<FocusOut>).
    - Safe to call on disabled widgets (silently skipped).
    - Uses `add="+"` so existing bindings are preserved.

    Parameters
    ----------
    widget : CTkEntry | CTkTextbox | tk.Entry | tk.Text
        The input widget to bind.

    Example
    -------
        from ui.keyboard_utils import bind_keyboard

        self.phone_entry = ctk.CTkEntry(parent, ...)
        bind_keyboard(self.phone_entry)
    """
    try:
        # CTkEntry wraps an internal tk.Entry accessible via ._entry
        # Fall back to the widget itself for plain tk widgets.
        inner = getattr(widget, "_entry", widget)
        inner.bind("<FocusIn>",  lambda _e: show_keyboard(), add="+")
        inner.bind("<FocusOut>", lambda _e: hide_keyboard(), add="+")
    except Exception as e:
        print(f"[keyboard_utils] bind_keyboard failed for {widget}: {e}")
