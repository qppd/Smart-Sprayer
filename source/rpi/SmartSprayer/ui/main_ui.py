# main_ui.py
# Sprayer System GUI – Image Matched Layout

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.hardware_interface import get_hardware
from core.logger import get_logger
from core.data_store import get_data_store
from core.scheduler import get_scheduler
from core.reschedule_logic import get_reschedule_manager

# Module-level flag set by _request_logout so main() can return "logout"
_logout_requested = False

from ui.dashboard import DashboardPanel
from ui.scheduling import SchedulingPanel
from ui.previous_data import PreviousDataPanel
from ui.notifications import NotificationsPanel
from ui.settings import SettingsFrame
from ui.account import SprayerAccountPanel
from ui.keyboard_utils import attach_floating_icon, bind_all_entries



class SmartSprayerUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window — fixed 1024×600, not resizable / minimizable / maximizable
        self.title("Sprayer System Control")
        self.geometry("1024x600")
        self.resizable(False, False)
        # Center the window on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"1024x600+{(sw - 1024) // 2}+{(sh - 600) // 2}")
        # Prevent minimize and maximize (intercept Iconify / Zoom state changes)
        self.bind("<Unmap>", lambda e: self.deiconify() if str(e.widget) == str(self) else None)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Core
        self.logger = get_logger()
        self.hardware = get_hardware()
        self.data_store = get_data_store()
        self.scheduler = get_scheduler(self.hardware)
        self.reschedule_mgr = get_reschedule_manager()

        self.scheduler.start()
        self._sync_esp32_on_startup()

        # ---------------- COLOR PALETTE ----------------
        self.COL_TOPBAR_BG = "#ECF6F1"
        self.COL_SIDEBAR_BG = "#EDF7F2"
        self.COL_CONTENT_BG = "#F6FBF9"

        self.COL_TEXT_DARK = "#1B5E20"
        self.COL_TEXT_MID = "#2E7D32"
        self.COL_TEXT_GRAY = "#6D6D6D"

        self.COL_ACTIVE_BG = "#D6EEE0"
        self.COL_ACTIVE_BAR = "#4CAF50"
        self.COL_HOVER = "#E4F5EC"

        self.COL_DIVIDER = "#CDE6D7"

        self._create_ui()
        attach_floating_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    # =====================================================

    def _create_ui(self):

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ================= TOP BAR =================
        self.topbar = ctk.CTkFrame(
            self,
            fg_color=self.COL_TOPBAR_BG,
            height=120,
            corner_radius=0
        )
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.topbar.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(self.topbar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=28, pady=20)

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

        self.logo_img = None

        if os.path.exists(logo_path):
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(72, 72)
            )

        ctk.CTkLabel(left, text="", image=self.logo_img).grid(row=0, column=0, padx=(0, 18))

        ctk.CTkLabel(
            left,
            text="AUTOMATED SPRAYER SYSTEM",
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color=self.COL_TEXT_DARK
        ).grid(row=0, column=1, sticky="w")

        self.datetime_lbl = ctk.CTkLabel(
            self.topbar,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.COL_TEXT_GRAY
        )
        self.datetime_lbl.grid(row=0, column=1, sticky="e", padx=28)

        self._update_clock()

        divider = ctk.CTkFrame(self, height=2, fg_color=self.COL_DIVIDER)
        divider.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(118, 0))

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(
            self,
            width=420,
            fg_color=self.COL_SIDEBAR_BG,
            corner_radius=0
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)

        self.nav_buttons = {}
        self.nav_indicators = {}

        # Load navigation icons
        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")

        nav_items = [
            ("Dashboard",     "dashboard",     "dashboard.png"),
            ("Scheduling",    "scheduling",    "scheduling.png"),
            ("Previous Data", "previous_data", "previous.png"),
            ("Notifications", "notifications", "notifications.png"),
            ("Settings",      "settings",      "settings.png"),
        ]

        for i, (label, key, icon_file) in enumerate(nav_items):

            container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            container.grid(row=i, column=0, sticky="ew",
                           padx=16, pady=(20 if i == 0 else 10, 0))
            container.grid_columnconfigure(1, weight=1)

            indicator = ctk.CTkFrame(
                container,
                width=8,
                height=72,
                fg_color="transparent",
                corner_radius=6
            )
            indicator.grid(row=0, column=0, sticky="ns", padx=(0, 14))

            # Try to load icon image
            icon_img = None
            icon_path = os.path.join(icons_path, icon_file)
            if os.path.exists(icon_path):
                try:
                    icon_img = ctk.CTkImage(
                        light_image=Image.open(icon_path),
                        dark_image=Image.open(icon_path),
                        size=(36, 36)
                    )
                except:
                    pass

            btn = ctk.CTkButton(
                container,
                text=f"  {label}",
                image=icon_img,
                compound="left",
                height=72,
                corner_radius=10,
                fg_color="transparent",
                text_color=self.COL_TEXT_MID,
                hover_color=self.COL_HOVER,
                font=ctk.CTkFont(size=32, weight="bold"),
                anchor="w",
                command=lambda k=key: self._show_panel(k)
            )
            btn.grid(row=0, column=1, sticky="ew")

            self.nav_buttons[key] = btn
            self.nav_indicators[key] = indicator

        # Account button with icon
        account_icon = None
        account_icon_path = os.path.join(icons_path, "account.png")
        if os.path.exists(account_icon_path):
            try:
                account_icon = ctk.CTkImage(
                    light_image=Image.open(account_icon_path),
                    dark_image=Image.open(account_icon_path),
                    size=(36, 36)
                )
            except:
                pass

        account_btn = ctk.CTkButton(
            self.sidebar,
            text="  Sprayer Account",
            image=account_icon,
            compound="left",
            height=72,
            corner_radius=10,
            fg_color="transparent",
            text_color=self.COL_TEXT_MID,
            hover_color=self.COL_HOVER,
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w",
            command=self._show_account
        )
        account_btn.grid(row=21, column=0, sticky="ew", padx=16, pady=(0, 24))

        # ================= CONTENT =================
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=self.COL_CONTENT_BG,
            corner_radius=0
        )
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.panels = {
            "dashboard":    DashboardPanel(self.content_frame, self.hardware, self.scheduler),
            "scheduling":   SchedulingPanel(self.content_frame, self.scheduler, self.reschedule_mgr, self.logger),
            "previous_data": PreviousDataPanel(self.content_frame, self.data_store),
            "notifications": NotificationsPanel(self.content_frame, self.scheduler, self.data_store, self.hardware),
            "settings":     SettingsFrame(self.content_frame),
            "account":      SprayerAccountPanel(self.content_frame)
        }

        self._show_panel("dashboard")

    # =====================================================

    def _update_clock(self):
        now = datetime.now()
        formatted = now.strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.datetime_lbl.configure(text=formatted)
        self.after(1000, self._update_clock)

    # =====================================================

    def _show_panel(self, key):

        for panel in self.panels.values():
            panel.pack_forget()

        for k in self.nav_buttons:
            self.nav_buttons[k].configure(
                fg_color="transparent",
                text_color=self.COL_TEXT_MID
            )
            self.nav_indicators[k].configure(fg_color="transparent")

        self.panels[key].pack(fill="both", expand=True)
        if key in self.nav_buttons:
            self.nav_buttons[key].configure(
                fg_color=self.COL_ACTIVE_BG,
                text_color=self.COL_TEXT_DARK
            )
            self.nav_indicators[key].configure(
                fg_color=self.COL_ACTIVE_BAR
            )
        # Ensure every text field in the newly shown panel gets keyboard binding
        try:
            bind_all_entries(self.panels[key])
        except Exception:
            pass

    # =====================================================

    def _sync_esp32_on_startup(self):
        try:
            if self.hardware and self.hardware.connected:
                self.hardware.sync_time()

                from core.data_store import get_recipients
                recipients = get_recipients()
                phones = [r.get("phone") for r in recipients if r.get("phone")]
                self.hardware.sync_recipients_bulk(phones)
        except Exception as e:
            self.logger.log_error(f"ESP32 sync failed: {e}")

    # =====================================================

    def _show_account(self):
        self._show_panel("account")
        # Refresh account info every time the panel is opened
        try:
            self.panels["account"].refresh()
        except Exception as e:
            print(f"[ACCOUNT] Refresh error: {e}")

    def _request_logout(self):
        """Called by the account panel when the user confirms logout."""
        global _logout_requested
        _logout_requested = True
        try:
            self.scheduler.stop()
        except Exception:
            pass
        try:
            if self.hardware:
                self.hardware.cleanup()
        except Exception:
            pass
        self.destroy()

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Exit Sprayer System?"):
            self.scheduler.stop()
            if self.hardware:
                self.hardware.cleanup()
            self.destroy()


def main():
    global _logout_requested
    _logout_requested = False
    app = SmartSprayerUI()
    app.mainloop()
    return "logout" if _logout_requested else None


if __name__ == "__main__":
    main()
