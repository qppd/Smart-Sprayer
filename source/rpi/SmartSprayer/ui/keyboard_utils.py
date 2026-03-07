# keyboard_utils.py
# Onboard virtual keyboard auto-show/hide helpers for SmartSprayerV2
#
# Public API
# ----------
#   bind_keyboard(widget)       – auto-show on focus-in, hide on focus-out
#   show_keyboard()             – show Onboard explicitly
#   hide_keyboard()             – terminate Onboard
#   attach_floating_icon(root)  – add a floating "⌨" button that reopens the
#                                  keyboard and auto-hides when KB is visible
#   bind_all_entries(container) – walk widget tree and call bind_keyboard on
#                                  every Entry / CTkEntry / CTkTextbox found
#
# Behaviour notes
# ---------------
# • Onboard is launched with --keep-aspect and stays always-on-top via its
#   own `--keep-on-top` flag, so it floats above the Smart-Sprayer GUI.
# • The floating icon appears at bottom-right when the keyboard is dismissed
#   while a text field is still focused. A tap reopens the keyboard.
# • All functions silently no-op on non-Linux platforms (safe for dev machines).

import subprocess
import sys
import tkinter as tk

# ── platform guard ────────────────────────────────────────────────────────────
_IS_LINUX = sys.platform.startswith("linux")

_onboard_proc: "subprocess.Popen | None" = None
_keyboard_visible: bool = False

# Tkinter root reference used for the floating icon (set by attach_floating_icon)
_root_ref: "tk.Misc | None" = None
_float_icon_win: "tk.Toplevel | None" = None


def show_keyboard():
    """
    Launch the Onboard virtual keyboard if it is not already running.

    Features:
    - Uses --keep-on-top so Onboard floats above the application window.
    - Phone layout is compact and touch-friendly.
    - Safe to call repeatedly; nop if already running.
    """
    if not _IS_LINUX:
        return

    global _onboard_proc, _keyboard_visible
    try:
        if _onboard_proc is not None and _onboard_proc.poll() is None:
            _keyboard_visible = True
            _hide_float_icon()
            return
        _onboard_proc = subprocess.Popen(
            [
                "onboard",
                "--size=800x280",
                "--layout=Phone",
                "--theme=Nightshade",
                "--keep-on-top",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _keyboard_visible = True
        _hide_float_icon()
    except FileNotFoundError:
        print("[keyboard_utils] Onboard not found — install with: sudo apt install onboard")
    except Exception as e:
        print(f"[keyboard_utils] Could not launch Onboard: {e}")


def hide_keyboard():
    """
    Terminate the Onboard virtual keyboard.

    Shows the floating re-open icon (if a root window was registered via
    attach_floating_icon) so the user can easily reopen it.
    """
    if not _IS_LINUX:
        return

    global _onboard_proc, _keyboard_visible
    try:
        if _onboard_proc is not None and _onboard_proc.poll() is None:
            _onboard_proc.terminate()
    except Exception as e:
        print(f"[keyboard_utils] Could not terminate Onboard: {e}")
    finally:
        _onboard_proc = None
        _keyboard_visible = False
        _show_float_icon()


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
    """
    try:
        inner = getattr(widget, "_entry", widget)
        inner.bind("<FocusIn>",  lambda _e: show_keyboard(), add="+")
        inner.bind("<FocusOut>", lambda _e: _on_focus_out(), add="+")
    except Exception as e:
        print(f"[keyboard_utils] bind_keyboard failed for {widget}: {e}")


def bind_all_entries(container):
    """
    Walk the widget tree rooted at *container* and call bind_keyboard on every
    Entry, CTkEntry, and CTkTextbox found.  Safe to call on any frame or window.

    Useful for screens that build lots of fields dynamically or that import
    third-party panels without manually binding each widget.
    """
    try:
        _recurse_bind(container)
    except Exception as e:
        print(f"[keyboard_utils] bind_all_entries error: {e}")


def attach_floating_icon(root):
    """
    Register a root/Toplevel window so a floating keyboard icon button can be
    shown there whenever the keyboard is hidden while the user is still editing.

    The icon sits at the bottom-right corner of the screen and has -topmost so
    it always stays visible.  Clicking it calls show_keyboard().

    Parameters
    ----------
    root : tk.Tk | ctk.CTk | tk.Toplevel
        The application's main window.
    """
    global _root_ref
    _root_ref = root


# ── internal helpers ──────────────────────────────────────────────────────────

def _on_focus_out():
    """Called when a bound widget loses focus. Hides keyboard and shows icon."""
    if not _IS_LINUX:
        return
    # Only hide if no other text widget just grabbed focus (small delay avoids
    # flickering when tabbing between fields).
    if _root_ref is not None:
        try:
            _root_ref.after(150, _maybe_hide_keyboard)
        except Exception:
            hide_keyboard()
    else:
        hide_keyboard()


def _maybe_hide_keyboard():
    """Hides keyboard only if the currently focused widget is NOT an entry."""
    if not _IS_LINUX:
        return
    try:
        if _root_ref is None:
            hide_keyboard()
            return
        focused = _root_ref.focus_get()
        if focused is None:
            hide_keyboard()
            return
        # If focused widget is an Entry or Text, keep keyboard open
        widget_class = focused.winfo_class()
        if widget_class in ("Entry", "Text", "TEntry"):
            return
        hide_keyboard()
    except Exception:
        hide_keyboard()


def _show_float_icon():
    """Display a small always-on-top floating button to reopen the keyboard."""
    if not _IS_LINUX or _root_ref is None:
        return
    global _float_icon_win
    try:
        if _float_icon_win is not None:
            try:
                _float_icon_win.deiconify()
                return
            except Exception:
                _float_icon_win = None

        win = tk.Toplevel(_root_ref)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg="#2E7D32")

        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        size = 72
        win.geometry(f"{size}x{size}+{sw - size - 20}+{sh - size - 20}")

        btn = tk.Button(
            win,
            text="⌨",
            font=("Segoe UI", 30),
            bg="#2E7D32",
            fg="white",
            relief="flat",
            activebackground="#388E3C",
            activeforeground="white",
            bd=0,
            command=show_keyboard,
            cursor="hand2",
        )
        btn.place(relx=0.5, rely=0.5, anchor="center")

        _float_icon_win = win
    except Exception as e:
        print(f"[keyboard_utils] Could not create floating icon: {e}")


def _hide_float_icon():
    """Hide the floating keyboard icon (keyboard is now open)."""
    global _float_icon_win
    try:
        if _float_icon_win is not None:
            _float_icon_win.withdraw()
    except Exception:
        _float_icon_win = None


def _recurse_bind(widget):
    """Recursively bind keyboard to all entry-like widgets in widget tree."""
    cls = getattr(widget, "__class__", None)
    cls_name = cls.__name__ if cls else ""
    tk_class = ""
    try:
        tk_class = widget.winfo_class()
    except Exception:
        pass

    is_entry = (
        tk_class in ("Entry", "Text", "TEntry")
        or "Entry" in cls_name
        or "Textbox" in cls_name
    )
    if is_entry:
        bind_keyboard(widget)

    try:
        for child in widget.winfo_children():
            _recurse_bind(child)
    except Exception:
        pass

