# account.py
# Sprayer Account Panel – Account info display/edit, security, logout

import customtkinter as ctk
from datetime import datetime

from core.session import (
    get_username, get_phone, set_phone,
    get_status, set_status,
    get_last_login, get_created_at,
    get_password, set_password, verify_password,
    clear_session,
)

# ══════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════
GREEN      = "#43A047"
DARK_GREEN = "#1B5E20"
GRAY       = "#757575"
LIGHT_BG   = "#F4FBF7"
CARD_BG    = "#FFFFFF"
RED        = "#E53935"
BLUE       = "#1E88E5"
DIVIDER    = "#E8F5E9"
BG         = "#F3F8F6"


# ══════════════════════════════════════════════════════
# SHARED MODAL HELPER
# ══════════════════════════════════════════════════════

def _base_modal(parent, w=620, h=440):
    modal = ctk.CTkToplevel(parent)
    modal.overrideredirect(True)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F5F5F5")
    x = (modal.winfo_screenwidth()  // 2) - (w // 2)
    y = (modal.winfo_screenheight() // 2) - (h // 2)
    modal.geometry(f"{w}x{h}+{x}+{y}")
    outer = ctk.CTkFrame(modal, fg_color=DIVIDER, corner_radius=22)
    outer.pack(fill="both", expand=True, padx=3, pady=3)
    container = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=20)
    container.pack(fill="both", expand=True, padx=2, pady=2)
    return modal, container


def show_error_modal(parent, title, message):
    modal, container = _base_modal(parent)

    icon_frame = ctk.CTkFrame(container, fg_color="#FFEBEE",
                               width=88, height=88, corner_radius=999)
    icon_frame.pack_propagate(False)
    icon_frame.pack(pady=(30, 12))
    ctk.CTkLabel(icon_frame, text="✕",
                 font=ctk.CTkFont(size=36, weight="bold"),
                 text_color=RED).pack(expand=True)

    ctk.CTkLabel(container, text=title,
                 font=ctk.CTkFont(size=34, weight="bold"),
                 text_color="#2E2E2E").pack(pady=(0, 10))

    ctk.CTkLabel(container, text=message,
                 font=ctk.CTkFont(size=26),
                 text_color="#4A4A4A",
                 wraplength=540, justify="center").pack(pady=(0, 24))

    ctk.CTkButton(container, text="OK",
                  width=240, height=62, corner_radius=12,
                  font=ctk.CTkFont(size=28, weight="bold"),
                  fg_color=RED, hover_color="#C62828",
                  command=modal.destroy).pack()
    modal.wait_window()


def show_success_modal(parent, title, message):
    modal, container = _base_modal(parent)

    icon_frame = ctk.CTkFrame(container, fg_color="#E8F5E9",
                               width=88, height=88, corner_radius=999)
    icon_frame.pack_propagate(False)
    icon_frame.pack(pady=(30, 12))
    ctk.CTkLabel(icon_frame, text="✓",
                 font=ctk.CTkFont(size=36, weight="bold"),
                 text_color=GREEN).pack(expand=True)

    ctk.CTkLabel(container, text=title,
                 font=ctk.CTkFont(size=34, weight="bold"),
                 text_color="#2E2E2E").pack(pady=(0, 10))

    ctk.CTkLabel(container, text=message,
                 font=ctk.CTkFont(size=26),
                 text_color="#4A4A4A",
                 wraplength=540, justify="center").pack(pady=(0, 24))

    ctk.CTkButton(container, text="OK",
                  width=240, height=62, corner_radius=12,
                  font=ctk.CTkFont(size=28, weight="bold"),
                  fg_color=GREEN, hover_color="#388E3C",
                  command=modal.destroy).pack()
    modal.wait_window()


# ══════════════════════════════════════════════════════
# PANEL
# ══════════════════════════════════════════════════════

class SprayerAccountPanel(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._value_labels = {}   # field key → CTkLabel for live refresh
        self._create_ui()

    # ── helpers ──────────────────────────────────────

    def _card(self, parent):
        return ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=20)

    def _card_title(self, parent, text):
        ctk.CTkFrame(parent, fg_color=DARK_GREEN, height=5,
                     corner_radius=0).pack(fill="x")
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=38, weight="bold"),
                     text_color=DARK_GREEN).pack(anchor="w", padx=30, pady=(22, 18))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=DIVIDER, height=2).pack(
            fill="x", padx=30, pady=6)

    # ── main layout ──────────────────────────────────

    def _create_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=(30, 10))
        wrapper.grid_columnconfigure((0, 1), weight=1)

        # ── LEFT: Account Info ─────────────────────────
        left = self._card(wrapper)
        left.grid(row=0, column=0, sticky="new", padx=(0, 16))

        self._card_title(left, "Account Information")

        avatar_frame = ctk.CTkFrame(left, fg_color=LIGHT_BG,
                                    corner_radius=999, width=108, height=108)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(pady=(0, 18))
        ctk.CTkLabel(avatar_frame, text="👤",
                     font=ctk.CTkFont(size=54)).pack(expand=True)

        # Read-only info rows
        self._info_row(left, "Username",   get_username() or "sprayer", "username")
        self._info_row(left, "Role",       "Built-in Device Account",   None)

        # Editable info rows
        self._info_editable_row(left, "Phone",  get_phone() or "Not Set",
                                "phone",  self._edit_phone)
        self._info_editable_row(left, "Status", get_status() or "Active",
                                "status", self._edit_status,
                                value_color=GREEN)

        self._info_row(left, "Created",    get_created_at(), "created_at")
        self._info_row(left, "Last Login", get_last_login(), "last_login")

        ctk.CTkFrame(left, fg_color="transparent", height=24).pack()

        # ── RIGHT: Security ────────────────────────────
        right = self._card(wrapper)
        right.grid(row=0, column=1, sticky="new")

        self._card_title(right, "Security")
        self._divider(right)

        self.current_pass = self._password_field(right, "Current Password")
        self.new_pass     = self._password_field(right, "New Password")
        self.confirm_pass = self._password_field(right, "Confirm Password")

        ctk.CTkButton(
            right, text="Change Password",
            height=64, corner_radius=13,
            fg_color=GREEN, hover_color="#388E3C",
            font=ctk.CTkFont(size=28, weight="bold"),
            command=self._change_password
        ).pack(fill="x", padx=30, pady=(12, 30))

        # ── Logout ─────────────────────────────────────
        logout_row = ctk.CTkFrame(self, fg_color="transparent")
        logout_row.pack(fill="x", padx=40, pady=(24, 44))

        ctk.CTkButton(
            logout_row, text="Log Out",
            height=60, width=240, corner_radius=12,
            fg_color="#FFEBEE", text_color=RED,
            hover_color="#FFCDD2",
            border_width=1, border_color="#FFCDD2",
            font=ctk.CTkFont(size=26, weight="bold"),
            command=self._logout
        ).pack(anchor="center")

    # ── info row (read-only) ──────────────────────────

    def _info_row(self, parent, label, value, key=None):
        row = ctk.CTkFrame(parent, fg_color=LIGHT_BG, corner_radius=12)
        row.pack(fill="x", padx=30, pady=6)

        ctk.CTkLabel(row, text=label, text_color=GRAY,
                     font=ctk.CTkFont(size=26)).pack(side="left", padx=20, pady=16)

        val_lbl = ctk.CTkLabel(row, text=value, text_color=DARK_GREEN,
                               font=ctk.CTkFont(size=26, weight="bold"))
        val_lbl.pack(side="right", padx=20, pady=16)

        if key:
            self._value_labels[key] = val_lbl

    # ── info row (editable) ───────────────────────────

    def _info_editable_row(self, parent, label, value, key, edit_cmd,
                           value_color=None):
        row = ctk.CTkFrame(parent, fg_color=LIGHT_BG, corner_radius=12)
        row.pack(fill="x", padx=30, pady=6)

        ctk.CTkLabel(row, text=label, text_color=GRAY,
                     font=ctk.CTkFont(size=26)).pack(side="left", padx=20, pady=16)

        ctk.CTkButton(
            row, text="Edit",
            width=90, height=42, corner_radius=8,
            fg_color=DARK_GREEN, hover_color="#163A1B",
            font=ctk.CTkFont(size=22, weight="bold"),
            command=edit_cmd
        ).pack(side="right", padx=14, pady=16)

        val_lbl = ctk.CTkLabel(row, text=value,
                               text_color=value_color or DARK_GREEN,
                               font=ctk.CTkFont(size=26, weight="bold"))
        val_lbl.pack(side="right", padx=(0, 8), pady=16)

        if key:
            self._value_labels[key] = val_lbl

    # ── password field ────────────────────────────────

    def _password_field(self, parent, label):
        ctk.CTkLabel(parent, text=label, text_color=GRAY,
                     font=ctk.CTkFont(size=26)).pack(anchor="w", padx=30, pady=(12, 4))
        entry = ctk.CTkEntry(
            parent, show="•", height=60, corner_radius=12,
            font=ctk.CTkFont(size=26)
        )
        entry.pack(fill="x", padx=30, pady=(0, 4))
        return entry

    # ══════════════════════════════════════════════════
    # REFRESH
    # ══════════════════════════════════════════════════

    def refresh(self):
        """Reload all account info from storage and update displayed labels."""
        updates = {
            "username":   get_username()   or "sprayer",
            "phone":      get_phone()      or "Not Set",
            "status":     get_status()     or "Active",
            "created_at": get_created_at(),
            "last_login": get_last_login(),
        }
        for key, val in updates.items():
            if key in self._value_labels:
                self._value_labels[key].configure(text=val)

        # Recolor status label based on value
        if "status" in self._value_labels:
            color = GREEN if updates["status"] == "Active" else GRAY
            self._value_labels["status"].configure(text_color=color)

        # Clear password fields on every visit
        for entry in (self.current_pass, self.new_pass, self.confirm_pass):
            entry.delete(0, "end")

    # ══════════════════════════════════════════════════
    # EDIT PHONE
    # ══════════════════════════════════════════════════

    def _edit_phone(self):
        modal, container = _base_modal(self, w=640, h=420)

        ctk.CTkLabel(container, text="Edit Phone Number",
                     font=ctk.CTkFont(size=36, weight="bold"),
                     text_color=DARK_GREEN).pack(pady=(30, 6))
        ctk.CTkLabel(container,
                     text="Enter your mobile number (e.g. +639XXXXXXXXX)",
                     font=ctk.CTkFont(size=24), text_color=GRAY).pack(pady=(0, 20))

        entry = ctk.CTkEntry(
            container, height=62, corner_radius=12,
            font=ctk.CTkFont(size=28),
            placeholder_text="+639XXXXXXXXX"
        )
        entry.pack(fill="x", padx=40, pady=(0, 8))

        current_phone = get_phone()
        if current_phone:
            entry.insert(0, current_phone)

        def _save():
            phone = entry.get().strip()
            if not phone:
                show_error_modal(modal, "Invalid", "Phone number cannot be empty.")
                return
            if not (phone.startswith("+") and len(phone) >= 10):
                show_error_modal(modal, "Invalid",
                                 "Enter a valid number starting with +\n(e.g. +639XXXXXXXXX).")
                return
            set_phone(phone)
            if "phone" in self._value_labels:
                self._value_labels["phone"].configure(text=phone)
            # Sync to ESP32 if connected
            try:
                from hardware.hardware_interface import get_hardware
                hw = get_hardware()
                if hw and hw.connected:
                    hw.send_sms(phone,
                        "Smart Sprayer: Your phone number has been updated successfully.")
            except Exception as e:
                print(f"⚠️ Phone sync error: {e}")
            modal.destroy()
            show_success_modal(self, "Saved", "Phone number updated successfully.")

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=(14, 0))

        ctk.CTkButton(btn_row, text="Cancel", width=200, height=58,
                      corner_radius=12, fg_color="#E0E0E0",
                      text_color="#333", hover_color="#D6D6D6",
                      font=ctk.CTkFont(size=26, weight="bold"),
                      command=modal.destroy).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="Save", width=200, height=58,
                      corner_radius=12, fg_color=GREEN, hover_color="#388E3C",
                      font=ctk.CTkFont(size=26, weight="bold"),
                      command=_save).pack(side="left", padx=10)

        modal.wait_window()

    # ══════════════════════════════════════════════════
    # EDIT STATUS
    # ══════════════════════════════════════════════════

    def _edit_status(self):
        modal, container = _base_modal(self, w=580, h=380)

        ctk.CTkLabel(container, text="Account Status",
                     font=ctk.CTkFont(size=36, weight="bold"),
                     text_color=DARK_GREEN).pack(pady=(30, 6))
        ctk.CTkLabel(container, text="Select the account status",
                     font=ctk.CTkFont(size=24), text_color=GRAY).pack(pady=(0, 24))

        status_var = ctk.StringVar(value=get_status() or "Active")

        radio_frame = ctk.CTkFrame(container, fg_color="transparent")
        radio_frame.pack(pady=(0, 20))

        ctk.CTkRadioButton(radio_frame, text="Active",
                           variable=status_var, value="Active",
                           font=ctk.CTkFont(size=28),
                           fg_color=GREEN).pack(side="left", padx=30)
        ctk.CTkRadioButton(radio_frame, text="Inactive",
                           variable=status_var, value="Inactive",
                           font=ctk.CTkFont(size=28),
                           fg_color=GRAY).pack(side="left", padx=30)

        def _save():
            new_status = status_var.get()
            set_status(new_status)
            if "status" in self._value_labels:
                color = GREEN if new_status == "Active" else GRAY
                self._value_labels["status"].configure(
                    text=new_status, text_color=color)
            modal.destroy()
            show_success_modal(self, "Saved", f"Status set to {new_status}.")

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(btn_row, text="Cancel", width=200, height=58,
                      corner_radius=12, fg_color="#E0E0E0",
                      text_color="#333", hover_color="#D6D6D6",
                      font=ctk.CTkFont(size=26, weight="bold"),
                      command=modal.destroy).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="Save", width=200, height=58,
                      corner_radius=12, fg_color=GREEN, hover_color="#388E3C",
                      font=ctk.CTkFont(size=26, weight="bold"),
                      command=_save).pack(side="left", padx=10)

        modal.wait_window()

    # ══════════════════════════════════════════════════
    # CHANGE PASSWORD
    # ══════════════════════════════════════════════════

    def _change_password(self):
        current = self.current_pass.get()
        new     = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if not current or not new or not confirm:
            show_error_modal(self, "Missing Fields",
                             "Please fill in all password fields.")
            return

        if not verify_password(current):
            show_error_modal(self, "Wrong Password",
                             "Current password is incorrect.")
            return

        if len(new) < 4:
            show_error_modal(self, "Too Short",
                             "New password must be at least 4 characters.")
            return

        if new != confirm:
            show_error_modal(self, "Mismatch",
                             "New passwords do not match.")
            return

        set_password(new)
        self.current_pass.delete(0, "end")
        self.new_pass.delete(0, "end")
        self.confirm_pass.delete(0, "end")
        show_success_modal(self, "Password Changed",
                           "Your password has been updated successfully.")

    # ══════════════════════════════════════════════════
    # LOGOUT
    # ══════════════════════════════════════════════════

    def _logout(self):
        modal, container = _base_modal(self, w=620, h=400)

        icon_frame = ctk.CTkFrame(container, fg_color="#FFEBEE",
                                   width=88, height=88, corner_radius=999)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(30, 12))
        ctk.CTkLabel(icon_frame, text="?",
                     font=ctk.CTkFont(size=46, weight="bold"),
                     text_color=RED).pack(expand=True)

        ctk.CTkLabel(container, text="Log Out",
                     font=ctk.CTkFont(size=38, weight="bold"),
                     text_color=DARK_GREEN).pack()

        ctk.CTkLabel(container,
                     text="Are you sure you want to log out?",
                     text_color=GRAY,
                     font=ctk.CTkFont(size=28)).pack(pady=(12, 26))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(btn_row, text="Cancel", width=240, height=62,
                      corner_radius=12, fg_color="#E0E0E0",
                      text_color="#333333", hover_color="#D6D6D6",
                      font=ctk.CTkFont(size=28, weight="bold"),
                      command=modal.destroy).pack(side="left", padx=12)

        ctk.CTkButton(btn_row, text="Log Out", width=240, height=62,
                      corner_radius=12, fg_color=RED, hover_color="#C62828",
                      font=ctk.CTkFont(size=28, weight="bold"),
                      command=lambda: self._confirm_logout(modal)
                      ).pack(side="left", padx=12)

        modal.wait_window()

    def _confirm_logout(self, modal):
        modal.destroy()
        clear_session()
        print("[ACCOUNT] User logged out — returning to login screen")
        # Tell SmartSprayerUI to do a clean shutdown and restart the login flow
        toplevel = self.winfo_toplevel()
        if hasattr(toplevel, "_request_logout"):
            toplevel._request_logout()
        else:
            toplevel.destroy()


import customtkinter as ctk
from datetime import datetime

from core.session import (
    get_username, get_phone, set_user, set_phone,
    get_last_login, get_created_at, clear_session,
    get_password, set_password, verify_password,
)

# ══════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════
GREEN      = "#43A047"
DARK_GREEN = "#1B5E20"
GRAY       = "#757575"
LIGHT_BG   = "#F4FBF7"
CARD_BG    = "#FFFFFF"
RED        = "#E53935"
BLUE       = "#1E88E5"
DIVIDER    = "#E8F5E9"
BG         = "#F3F8F6"


# ══════════════════════════════════════════════════════
# SHARED MODAL HELPER
# ══════════════════════════════════════════════════════

def _base_modal(parent, w=620, h=440):
    modal = ctk.CTkToplevel(parent)
    modal.overrideredirect(True)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F5F5F5")
    x = (modal.winfo_screenwidth()  // 2) - (w // 2)
    y = (modal.winfo_screenheight() // 2) - (h // 2)
    modal.geometry(f"{w}x{h}+{x}+{y}")
    outer = ctk.CTkFrame(modal, fg_color=DIVIDER, corner_radius=22)
    outer.pack(fill="both", expand=True, padx=3, pady=3)
    container = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=20)
    container.pack(fill="both", expand=True, padx=2, pady=2)
    return modal, container


def show_error_modal(parent, title, message):
    modal, container = _base_modal(parent)

    icon_frame = ctk.CTkFrame(container, fg_color="#FFEBEE",
                               width=88, height=88, corner_radius=999)
    icon_frame.pack_propagate(False)
    icon_frame.pack(pady=(30, 12))
    ctk.CTkLabel(icon_frame, text="X",
                 font=ctk.CTkFont(size=40, weight="bold"),
                 text_color=RED).pack(expand=True)

    ctk.CTkLabel(container, text=title,
                 font=ctk.CTkFont(size=34, weight="bold"),
                 text_color="#2E2E2E").pack(pady=(0, 10))

    ctk.CTkLabel(container, text=message,
                 font=ctk.CTkFont(size=28),
                 text_color="#4A4A4A",
                 wraplength=540).pack(pady=(0, 24))

    ctk.CTkButton(container, text="OK",
                  width=240, height=62,
                  corner_radius=12,
                  font=ctk.CTkFont(size=28, weight="bold"),
                  fg_color=RED, hover_color="#C62828",
                  command=modal.destroy).pack()

    modal.wait_window()


def show_success_modal(parent, title, message):
    modal, container = _base_modal(parent)

    icon_frame = ctk.CTkFrame(container, fg_color="#E8F5E9",
                               width=88, height=88, corner_radius=999)
    icon_frame.pack_propagate(False)
    icon_frame.pack(pady=(30, 12))
    ctk.CTkLabel(icon_frame, text="OK",
                 font=ctk.CTkFont(size=30, weight="bold"),
                 text_color=GREEN).pack(expand=True)

    ctk.CTkLabel(container, text=title,
                 font=ctk.CTkFont(size=34, weight="bold"),
                 text_color="#2E2E2E").pack(pady=(0, 10))

    ctk.CTkLabel(container, text=message,
                 font=ctk.CTkFont(size=28),
                 text_color="#4A4A4A",
                 wraplength=540).pack(pady=(0, 24))

    ctk.CTkButton(container, text="OK",
                  width=240, height=62,
                  corner_radius=12,
                  font=ctk.CTkFont(size=28, weight="bold"),
                  fg_color=GREEN, hover_color="#388E3C",
                  command=modal.destroy).pack()

    modal.wait_window()


# ══════════════════════════════════════════════════════
# PANEL
# ══════════════════════════════════════════════════════

class SprayerAccountPanel(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._create_ui()

    # ── helpers ──────────────────────────────────────

    def _card(self, parent):
        return ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=20)

    def _card_title(self, parent, text):
        strip = ctk.CTkFrame(parent, fg_color=DARK_GREEN, height=5, corner_radius=0)
        strip.pack(fill="x")
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=38, weight="bold"),
                     text_color=DARK_GREEN).pack(anchor="w", padx=30, pady=(22, 18))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=DIVIDER, height=2).pack(
            fill="x", padx=30, pady=6)

    # ── main layout ──────────────────────────────────

    def _create_ui(self):

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=40, pady=(30, 10))
        wrapper.grid_columnconfigure((0, 1), weight=1)

        # ── LEFT: Account Info ────────────────────────
        left = self._card(wrapper)
        left.grid(row=0, column=0, sticky="new", padx=(0, 16))

        self._card_title(left, "Account Information")

        # Avatar circle
        avatar_frame = ctk.CTkFrame(left, fg_color=LIGHT_BG,
                                    corner_radius=999, width=108, height=108)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(pady=(0, 18))
        ctk.CTkLabel(avatar_frame, text=" ",
                     font=ctk.CTkFont(size=54)).pack(expand=True)

        username   = get_username()  or "Not Set"
        phone      = get_phone()     or "Not Set"
        last_login = get_last_login()
        created_at = get_created_at()

        self._info(left, "Username",   username)
        self._info(left, "Role",       "Built-in Device Account")
        self._info(left, "Phone",      phone)
        self._info(left, "Status",     "Active",     value_color=GREEN)
        self._info(left, "Created",    created_at)
        self._info(left, "Last Login", last_login)

        ctk.CTkFrame(left, fg_color="transparent", height=24).pack()

        # ── RIGHT: Security ───────────────────────────
        right = self._card(wrapper)
        right.grid(row=0, column=1, sticky="new")

        self._card_title(right, "Security")

        self._divider(right)

        self.current_pass = self._password_field(right, "Current Password")
        self.new_pass     = self._password_field(right, "New Password")
        self.confirm_pass = self._password_field(right, "Confirm Password")

        ctk.CTkButton(
            right,
            text="Change Password",
            height=64,
            corner_radius=13,
            fg_color=GREEN,
            hover_color="#388E3C",
            font=ctk.CTkFont(size=28, weight="bold"),
            command=self._change_password
        ).pack(fill="x", padx=30, pady=(12, 30))

        # ── Logout ────────────────────────────────────
        logout_row = ctk.CTkFrame(self, fg_color="transparent")
        logout_row.pack(fill="x", padx=40, pady=(24, 44))

        ctk.CTkButton(
            logout_row,
            text="Log Out",
            height=60, width=240,
            corner_radius=12,
            fg_color="#FFEBEE",
            text_color=RED,
            hover_color="#FFCDD2",
            border_width=1,
            border_color="#FFCDD2",
            font=ctk.CTkFont(size=26, weight="bold"),
            command=self._logout
        ).pack(anchor="center")

    # ══════════════════════════════════════════════════════
    # INFO ROW
    # ══════════════════════════════════════════════════════

    def _info(self, parent, label, value, value_color=None):
        row = ctk.CTkFrame(parent, fg_color=LIGHT_BG, corner_radius=12)
        row.pack(fill="x", padx=30, pady=6)

        ctk.CTkLabel(row, text=label,
                     text_color=GRAY,
                     font=ctk.CTkFont(size=26)).pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(row, text=value,
                     text_color=value_color or DARK_GREEN,
                     font=ctk.CTkFont(size=26, weight="bold")).pack(side="right", padx=20, pady=16)

    # ══════════════════════════════════════════════════════
    # PASSWORD FIELD
    # ══════════════════════════════════════════════════════

    def _password_field(self, parent, label):
        ctk.CTkLabel(parent, text=label,
                     text_color=GRAY,
                     font=ctk.CTkFont(size=26)).pack(anchor="w", padx=30, pady=(12, 4))

        entry = ctk.CTkEntry(
            parent,
            show="•",
            height=60,
            corner_radius=12,
            font=ctk.CTkFont(size=26)
        )
        entry.pack(fill="x", padx=30, pady=(0, 4))
        return entry

    # ══════════════════════════════════════════════════════
    # CHANGE PASSWORD
    # ══════════════════════════════════════════════════════

    def _change_password(self):
        current = self.current_pass.get()
        new     = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if not current or not new or not confirm:
            show_error_modal(self, "Missing Fields",
                             "Please fill in all password fields.")
            return

        if not verify_password(current):
            show_error_modal(self, "Wrong Password",
                             "Current password is incorrect.")
            return

        if len(new) < 4:
            show_error_modal(self, "Too Short",
                             "New password must be at least 4 characters.")
            return

        if new != confirm:
            show_error_modal(self, "Mismatch",
                             "New passwords do not match.")
            return

        set_password(new)
        # Sync new password to Firebase RTDB immediately
        try:
            from core.firebase_service import get_firebase_service
            fb = get_firebase_service()
            if fb.connected:
                fb.update_password_in_rtdb(new)
        except Exception as e:
            print(f"⚠️ RTDB password sync error: {e}")

        self.current_pass.delete(0, "end")
        self.new_pass.delete(0, "end")
        self.confirm_pass.delete(0, "end")
        show_success_modal(self, "Password Changed",
                           "Your password has been updated successfully.")

    # ══════════════════════════════════════════════════════
    # LOGOUT MODAL
    # ══════════════════════════════════════════════════════

    def _logout(self):
        modal, container = _base_modal(self, w=620, h=400)

        icon_frame = ctk.CTkFrame(container, fg_color="#FFEBEE",
                                   width=88, height=88, corner_radius=999)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(30, 12))
        ctk.CTkLabel(icon_frame, text="?",
                     font=ctk.CTkFont(size=46, weight="bold"),
                     text_color=RED).pack(expand=True)

        ctk.CTkLabel(container, text="Log Out",
                     font=ctk.CTkFont(size=38, weight="bold"),
                     text_color=DARK_GREEN).pack()

        ctk.CTkLabel(container,
                     text="Are you sure you want to log out?",
                     text_color=GRAY,
                     font=ctk.CTkFont(size=28)).pack(pady=(12, 26))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=240, height=62,
            corner_radius=12,
            fg_color="#E0E0E0",
            text_color="#333333",
            hover_color="#D6D6D6",
            font=ctk.CTkFont(size=28, weight="bold"),
            command=modal.destroy
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            btn_row, text="Log Out",
            width=240, height=62,
            corner_radius=12,
            fg_color=RED,
            hover_color="#C62828",
            font=ctk.CTkFont(size=28, weight="bold"),
            command=lambda: self._confirm_logout(modal)
        ).pack(side="left", padx=12)

    def _confirm_logout(self, modal):
        modal.destroy()
        clear_session()
        print("[ACCOUNT] User logged out — returning to login screen")
        toplevel = self.winfo_toplevel()
        if hasattr(toplevel, "_request_logout"):
            toplevel._request_logout()
        else:
            toplevel.destroy()
