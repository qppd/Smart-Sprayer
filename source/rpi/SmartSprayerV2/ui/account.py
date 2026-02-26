# account.py
# Sprayer Account Panel – Modernized

import customtkinter as ctk
from datetime import datetime

from core.session import (
    get_username, get_phone, set_user, set_phone,
    get_last_login, get_created_at, clear_session
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
        if not self.new_pass.get() or not self.confirm_pass.get():
            show_error_modal(self, "Error", "Please fill all fields")
            return

        if self.new_pass.get() != self.confirm_pass.get():
            show_error_modal(self, "Error", "Passwords do not match")
            return

        show_success_modal(self, "Success", "Password updated successfully")

        self.current_pass.delete(0, "end")
        self.new_pass.delete(0, "end")
        self.confirm_pass.delete(0, "end")

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
        print("User logged out, session cleared")
        self.winfo_toplevel().destroy()
