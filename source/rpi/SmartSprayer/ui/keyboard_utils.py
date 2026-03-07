# keyboard_utils.py
# In-app virtual keyboard for SmartSprayerV2 (CustomTkinter)
#
# ┌─────────────────────────────────────────────────────────────────────┐
# │  KeyboardManager  (singleton per root window)                       │
# │                                                                     │
# │  Renders a 1024 × 200 px overlay at the bottom of the app window.  │
# │  Shows automatically when a CTkEntry / CTkTextbox receives focus,   │
# │  hides when focus leaves all text widgets (with a small delay to    │
# │  prevent flickering when tabbing between fields).                   │
# │                                                                     │
# │  PUBLIC API (module-level, backward-compatible)                     │
# │  ─────────────────────────────────────────────                      │
# │  attach_floating_icon(root)  – create / attach the manager to root  │
# │  bind_keyboard(widget)       – bind show/hide to one widget         │
# │  bind_all_entries(container) – bind all Entry widgets in a tree     │
# │  show_keyboard()             – force-show the keyboard              │
# │  hide_keyboard()             – force-hide the keyboard              │
# │                                                                     │
# │  ADDING TO A NEW PAGE                                               │
# │  ──────────────────────                                             │
# │  1. Import: from ui.keyboard_utils import bind_all_entries          │
# │  2. After building all widgets call: bind_all_entries(self)         │
# │     – or call bind_keyboard(entry) on individual entries.           │
# │  3. That's it. The KeyboardManager instance is a singleton shared   │
# │     across the whole app.                                           │
# └─────────────────────────────────────────────────────────────────────┘

import tkinter as tk
import customtkinter as ctk

# ── keyboard layout definition ────────────────────────────────────────────────
#  Each row is a list of (label, value, weight).
#  Special values: "backspace", "enter", "shift", "space"
#  weight controls relative width within the row (integer).

_ROWS_NORMAL = [
    # Row 0 – numbers + symbols
    [("1","1",1),("2","2",1),("3","3",1),("4","4",1),("5","5",1),
     ("6","6",1),("7","7",1),("8","8",1),("9","9",1),("0","0",1),
     ("-","-",1),("=","=",1),("⌫","backspace",2)],
    # Row 1 – QWERTY
    [("q","q",1),("w","w",1),("e","e",1),("r","r",1),("t","t",1),
     ("y","y",1),("u","u",1),("i","i",1),("o","o",1),("p","p",1),
     ("[","[",1),("]","]",1)],
    # Row 2 – ASDF + Enter
    [("a","a",1),("s","s",1),("d","d",1),("f","f",1),("g","g",1),
     ("h","h",1),("j","j",1),("k","k",1),("l","l",1),(";",";",1),
     ("'","'",1),("↵","enter",2)],
    # Row 3 – Shift + ZXCV
    [("⇧","shift",2),("z","z",1),("x","x",1),("c","c",1),("v","v",1),
     ("b","b",1),("n","n",1),("m","m",1),(",",",",1),(".",".",1),
     ("/","/",1),("⇧","shift",2)],
    # Row 4 – Space row
    [("@","@",1),("_","_",1),("−","−",1),("        space        ","space",8),
     ("!","!",1),("?","?",1)],
]

_ROWS_SHIFTED = [
    [("!","!",1),("@","@",1),("#","#",1),("$","$",1),("%","%",1),
     ("^","^",1),("&","&",1),("*","*",1),("(","(",1),(")",  ")",1),
     ("_","_",1),("+","+",1),("⌫","backspace",2)],
    [("Q","Q",1),("W","W",1),("E","E",1),("R","R",1),("T","T",1),
     ("Y","Y",1),("U","U",1),("I","I",1),("O","O",1),("P","P",1),
     ("{","{",1),("}","}",1)],
    [("A","A",1),("S","S",1),("D","D",1),("F","F",1),("G","G",1),
     ("H","H",1),("J","J",1),("K","K",1),("L","L",1),(":",":",1),
     ('"','"',1),("↵","enter",2)],
    [("⇧","shift",2),("Z","Z",1),("X","X",1),("C","C",1),("V","V",1),
     ("B","B",1),("N","N",1),("M","M",1),("<","<",1),(">",">",1),
     ("?","?",1),("⇧","shift",2)],
    [("@","@",1),("_","_",1),("−","−",1),("        space        ","space",8),
     ("!","!",1),("?","?",1)],
]

# ── colors ────────────────────────────────────────────────────────────────────
_KB_BG       = "#1B3A22"   # dark green background
_KEY_BG      = "#2E7D32"   # normal key face
_KEY_HOVER   = "#388E3C"
_KEY_ACTIVE  = "#4CAF50"   # shift-on indicator
_KEY_TEXT    = "#FFFFFF"
_SPECIAL_BG  = "#1B5E20"   # backspace / enter background
_KEY_FONT    = ("Segoe UI", 16, "bold")


class KeyboardManager:
    """
    In-app virtual keyboard overlay (1024 × 200 px at y = 400).

    Instantiate once via attach_floating_icon(root) and then call
    bind_keyboard() or bind_all_entries() on any page you want covered.

    To attach to a new page:
        from ui.keyboard_utils import bind_all_entries
        bind_all_entries(my_new_frame)
    """

    KB_W = 1024
    KB_H = 200

    # Small ⌨ icon visible at bottom-right when keyboard is hidden but
    # the user previously focused a text entry.
    _ICON_SIZE = 48

    def __init__(self, root: tk.Misc):
        self._root = root
        self._visible = False
        self._shift   = False
        self._target: "tk.Widget | None" = None
        self._frame: "ctk.CTkFrame | None" = None
        self._row_frames: list = []
        self._key_buttons: list[list] = []   # [row][col] → CTkButton
        self._toggle_btn: "ctk.CTkButton | None" = None  # floating ⌨ icon
        self._had_focus: bool = False         # True once any entry was focused
        self._build_keyboard()
        self._build_toggle_icon()

    # ── public ────────────────────────────────────────────────────────────────

    def bind_entry(self, widget):
        """
        Attach show/hide to *widget* (CTkEntry, CTkTextbox, tk.Entry, tk.Text).
        Safe to call multiple times on the same widget (uses add="+").

        # To add keyboard support to a new entry in any page, call:
        #     bind_entry(my_entry)
        # or use the module-level convenience: bind_keyboard(my_entry)
        """
        try:
            inner = self._inner(widget)
            inner.bind("<FocusIn>",  lambda e: self._on_focus_in(widget),  add="+")
            inner.bind("<FocusOut>", lambda e: self._on_focus_out(),        add="+")
        except Exception as exc:
            print(f"[KeyboardManager] bind_entry failed for {widget}: {exc}")

    def bind_all(self, container):
        """
        Walk *container* recursively and call bind_entry on every
        Entry / CTkEntry / CTkTextbox found.
        """
        try:
            self._recurse(container)
        except Exception as exc:
            print(f"[KeyboardManager] bind_all error: {exc}")

    def show(self, target=None):
        """Show the keyboard and (optionally) set the target widget."""
        if target is not None:
            self._target = target
        if self._frame is None:
            return
        # Place at the very bottom of the root window
        self._frame.place(x=0, y=self._root.winfo_height() - self.KB_H)
        self._frame.lift()
        self._visible = True
        self._hide_toggle_icon()

    def hide(self):
        """Hide the keyboard."""
        if self._frame is not None:
            self._frame.place_forget()
        self._visible = False
        self._target  = None
        if self._had_focus:
            self._show_toggle_icon()

    def toggle(self, target=None):
        """Toggle visibility. Optionally set target widget."""
        if self._visible:
            self.hide()
        else:
            self.show(target)

    # ── keyboard construction ─────────────────────────────────────────────────

    def _build_keyboard(self):
        """Build the keyboard widget tree (initially hidden)."""
        self._frame = ctk.CTkFrame(
            self._root,
            fg_color=_KB_BG,
            corner_radius=0,
            width=self.KB_W,
            height=self.KB_H,
        )
        # Header strip: title label + close button
        header = ctk.CTkFrame(self._frame, fg_color=_KB_BG, height=24, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="⌨  Virtual Keyboard",
            text_color="#A5D6A7", font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            header, text="✕  Close",
            width=80, height=22,
            fg_color="#C62828", hover_color="#B71C1C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=4,
            command=self.hide,
        ).pack(side="right", padx=6, pady=1)
        # Don't place yet — keyboard starts hidden
        self._render_rows(_ROWS_NORMAL)

    def _build_toggle_icon(self):
        """Create a small persistent ⌨ icon button at bottom-right of the window.

        It is hidden initially and appears when the keyboard is dismissed while
        a text entry was previously focused, providing a manual re-open trigger.
        This button acts as the keyboard icon visible near text-entry fields.
        """
        s = self._ICON_SIZE
        rh = self._root.winfo_height() or 600
        x = self.KB_W - s - 8        # just inside right edge
        y = rh - self.KB_H - s - 8   # just above where keyboard would be
        self._toggle_btn = ctk.CTkButton(
            self._root,
            text="⌨",
            width=s,
            height=s,
            corner_radius=s // 2,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=24),
            command=lambda: self.show(self._target),
        )
        # Not placed yet — appears only after first entry interaction

    def _render_rows(self, rows):
        """Destroy old button grid and render *rows*."""
        for rf in self._row_frames:
            rf.destroy()
        self._row_frames.clear()
        self._key_buttons.clear()

        for row_spec in rows:
            rf = ctk.CTkFrame(self._frame, fg_color="transparent")
            rf.pack(fill="x", expand=True, padx=3, pady=1)
            row_btns: list = []

            for col, (label, value, weight) in enumerate(row_spec):
                rf.columnconfigure(col, weight=weight)
                is_special = value in ("backspace", "enter", "shift", "space")
                bg = _SPECIAL_BG if value in ("backspace", "enter") else (
                    _KEY_ACTIVE if (value == "shift" and self._shift) else _KEY_BG
                )
                btn = ctk.CTkButton(
                    rf,
                    text=label,
                    font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                    fg_color=bg,
                    hover_color=_KEY_HOVER,
                    text_color=_KEY_TEXT,
                    corner_radius=6,
                    border_width=0,
                    command=lambda v=value: self._on_virtual_key(v),
                )
                btn.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
                row_btns.append(btn)

            self._row_frames.append(rf)
            self._key_buttons.append(row_btns)

    # ── key press handling ────────────────────────────────────────────────────

    def _on_virtual_key(self, value: str):
        if value == "shift":
            self._shift = not self._shift
            self._render_rows(_ROWS_SHIFTED if self._shift else _ROWS_NORMAL)
            if self._visible:
                self._frame.lift()
            return

        if value == "backspace":
            self._do_backspace()
            return

        if value == "enter":
            self._do_enter()
            return

        if value == "space":
            self._insert_char(" ")
            return

        # Regular character
        self._insert_char(value)
        # Auto-release shift after one letter
        if self._shift and len(value) == 1 and value.isalpha():
            self._shift = False
            self._render_rows(_ROWS_NORMAL)
            if self._visible:
                self._frame.lift()

    def _insert_char(self, char: str):
        w = self._target
        if w is None:
            return
        try:
            inner = self._inner_editable(w)
            inner.insert(tk.INSERT, char)
        except Exception as exc:
            print(f"[KeyboardManager] insert_char failed: {exc}")

    def _do_backspace(self):
        w = self._target
        if w is None:
            return
        try:
            inner = self._inner_editable(w)
            # For tk.Entry / tk.Text use delete with cursor
            inner.delete("insert-1c", tk.INSERT)
        except Exception:
            try:
                # Fallback: delete last character of full content
                text = w.get()
                if text:
                    w.delete(len(text) - 1, "end")
            except Exception as exc:
                print(f"[KeyboardManager] backspace failed: {exc}")

    def _do_enter(self):
        w = self._target
        if w is None:
            return
        try:
            # Fire the Return binding on the inner widget if any
            inner = self._inner(w)
            inner.event_generate("<Return>")
        except Exception:
            pass

    # ── focus handling ────────────────────────────────────────────────────────

    def _on_focus_in(self, widget):
        self._target = widget
        self._had_focus = True
        self.show(widget)

    def _on_focus_out(self):
        # Small delay so we don't flicker when moving between entry fields
        try:
            self._root.after(180, self._maybe_hide)
        except Exception:
            self.hide()

    def _maybe_hide(self):
        """Hide only if the currently focused widget is not a text entry."""
        try:
            focused = self._root.focus_get()
            if focused is None:
                self.hide()
                return
            wclass = focused.winfo_class()
            if wclass in ("Entry", "Text", "TEntry"):
                return          # another entry is active — stay visible
            self.hide()
        except Exception:
            self.hide()

    # ── toggle icon helpers ───────────────────────────────────────────────────

    def _show_toggle_icon(self):
        """Place the floating ⌨ toggle icon above the keyboard zone."""
        if self._toggle_btn is None:
            return
        try:
            s = self._ICON_SIZE
            rh = self._root.winfo_height() or 600
            y = rh - self.KB_H - s - 8
            x = self.KB_W - s - 8
            self._toggle_btn.place(x=x, y=y)
            self._toggle_btn.lift()
        except Exception as exc:
            print(f"[KeyboardManager] toggle icon show failed: {exc}")

    def _hide_toggle_icon(self):
        """Hide the floating ⌨ toggle icon."""
        if self._toggle_btn is not None:
            try:
                self._toggle_btn.place_forget()
            except Exception:
                pass

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _inner(widget) -> tk.Widget:
        """Return the underlying tk widget for FocusIn/Out binding."""
        return getattr(widget, "_entry",
               getattr(widget, "_textbox", widget))

    @staticmethod
    def _inner_editable(widget) -> tk.Widget:
        """Return the inner tk.Entry / tk.Text for insert/delete operations."""
        return getattr(widget, "_entry",
               getattr(widget, "_textbox", widget))

    def _recurse(self, widget):
        cls_name = type(widget).__name__
        tk_class = ""
        try:
            tk_class = widget.winfo_class()
        except Exception:
            pass

        if (tk_class in ("Entry", "Text", "TEntry")
                or "Entry" in cls_name
                or "Textbox" in cls_name):
            self.bind_entry(widget)

        try:
            for child in widget.winfo_children():
                self._recurse(child)
        except Exception:
            pass


# ── module-level singleton ────────────────────────────────────────────────────
# One KeyboardManager is created when attach_floating_icon(root) is called.
_manager: "KeyboardManager | None" = None


def attach_floating_icon(root):
    """
    Create the KeyboardManager singleton and attach it to *root*.

    Call this once from the main application window (SmartSprayerUI.__init__).
    All subsequent bind_keyboard / bind_all_entries calls use this instance.

    Parameters
    ----------
    root : ctk.CTk | tk.Tk
        The application's main window.
    """
    global _manager
    _manager = KeyboardManager(root)


def bind_keyboard(widget):
    """
    Bind the virtual keyboard to *widget* (CTkEntry, CTkTextbox, …).

    Auto-shows keyboard on focus-in, auto-hides on focus-out.
    Safe to call before attach_floating_icon() — silently deferred.
    """
    if _manager is not None:
        _manager.bind_entry(widget)


def bind_all_entries(container):
    """
    Walk *container*'s widget tree and bind the keyboard to every
    Entry / CTkEntry / CTkTextbox found.

    Call this at the end of any page/panel's __init__ to get full coverage:
        bind_all_entries(self)
    """
    if _manager is not None:
        _manager.bind_all(container)


def show_keyboard():
    """Force-show the virtual keyboard."""
    if _manager is not None:
        _manager.show()


def hide_keyboard():
    """Force-hide the virtual keyboard."""
    if _manager is not None:
        _manager.hide()

