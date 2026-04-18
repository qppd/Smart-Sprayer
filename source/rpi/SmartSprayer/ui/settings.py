# settings.py
# Smart Sprayer Settings Panel (Modernized)

import customtkinter as ctk
import sys, os
import subprocess
import threading
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_store import get_recipients, add_recipient, delete_recipient, save_location, get_location
from hardware.hardware_interface import get_hardware
from hardware.esp32_connection import (
    ESP32Connection,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
    STATE_ERROR,
    STATE_CONNECTING,
    _list_serial_ports,
)


# ══════════════════════════════════════════════════════
# DESIGN TOKENS — mirrors scheduling.py DS class
# ══════════════════════════════════════════════════════
class DS:
    G900 = "#1B5E20"
    G800 = "#2E7D32"
    G600 = "#388E3C"
    G500 = "#4CAF50"
    G400 = "#66BB6A"
    G200 = "#C8E6C9"
    G100 = "#E8F5E9"
    G50  = "#F1F8F2"

    WHITE = "#FFFFFF"
    N50   = "#F7F8F7"
    N100  = "#EEF0EE"
    N200  = "#D8DDD8"
    N400  = "#9AA89A"
    N600  = "#555F55"
    N800  = "#2A2F2A"

    AMBER   = "#F59E0B"
    AMBER_D = "#D97706"
    RED     = "#EF4444"
    RED_D   = "#DC2626"


def _font(size, weight="normal", family="Segoe UI"):
    return ctk.CTkFont(family=family, size=size,
                       weight=weight if weight != "normal" else "normal")


# Legacy palette aliases used in card/field styling
BG        = DS.G50
WHITE     = DS.WHITE
GREEN     = DS.G800
BTN_GREEN = DS.G500
RED       = DS.RED
FIELD_BG  = DS.G100
ARROW_GREEN = DS.G400
GRAY      = DS.N600
DIVIDER   = DS.G200


class SettingsFrame(ctk.CTkScrollableFrame):

    def __init__(self, parent, hardware=None):
        super().__init__(parent, fg_color=BG)
        self.pack(fill="both", expand=True)

        # Use the shared hardware instance passed in from main_ui.
        # Fall back to creating a local one only when run standalone (e.g. tests).
        self.hardware = hardware if hardware is not None else get_hardware()

        self.lucban_barangays = [
            "Barangay 1","Barangay 2","Barangay 3","Barangay 4","Barangay 5",
            "Barangay 6","Barangay 7","Barangay 8","Barangay 9","Barangay 10",
            "Abang","Aliliw","Atulinao","Ayuti","Igang","Kabatete","Kakawit",
            "Kalangay","Kalyaat","Kilib","Kulapi","Mahabang Parang","Malupak",
            "Manasa","May-It","Nagsinamo","Nalunao","Palola","Piis","Samil",
            "Tiawe","Tinamnan"
        ]

        self.lucena_barangays = [
            "Barangay 1","Barangay 2","Barangay 3","Barangay 4","Barangay 5",
            "Barangay 6","Barangay 7","Barangay 8","Barangay 9","Barangay 10",
            "Barangay 11","Bo. Amparo","Cotta","Dalahican","Domoit",
            "Gulang-Gulang","Ibabang Dupay","Ibabang Iyam","Ibabang Talim",
            "Ilayang Dupay","Ilayang Iyam","Ilayang Talim","Isabang",
            "Market View","Mayao Crossing","Mayao Castillo","Mayao Kanluran",
            "Mayao Parada","Mayao Silangan","Ransohan","Salinas",
            "Talao-Talao","Tapucan"
        ]

        self.create_weather_card()
        self.create_sms_card()
        self.create_wifi_card()
        self.create_esp32_card()

        # Enable mouse-wheel scrolling anywhere in the panel
        self._bind_mousewheel(self)

    # ══════════════════════════════════════════════════════
    # MOUSE-WHEEL SCROLL  (works without touching the scrollbar)
    # ══════════════════════════════════════════════════════

    def _bind_mousewheel(self, scrollable_frame):
        """Bind scroll events recursively on every widget and re-bind on layout changes."""

        def _scroll(event):
            try:
                scrollable_frame._parent_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )
            except Exception:
                pass

        def _scroll_up(event):
            try:
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            except Exception:
                pass

        def _scroll_down(event):
            try:
                scrollable_frame._parent_canvas.yview_scroll(1, "units")
            except Exception:
                pass

        def _bind_widget(widget):
            try:
                widget.bind("<MouseWheel>", _scroll,      add="+")
                widget.bind("<Button-4>",   _scroll_up,   add="+")
                widget.bind("<Button-5>",   _scroll_down, add="+")
                widget.bind(
                    "<Configure>",
                    lambda e: _rebind_children(widget),
                    add="+"
                )
            except Exception:
                pass
            for child in widget.winfo_children():
                _bind_widget(child)

        def _rebind_children(widget):
            for child in widget.winfo_children():
                _bind_widget(child)

        _bind_widget(scrollable_frame)

        # Also bind the underlying canvas directly
        try:
            scrollable_frame._parent_canvas.bind("<MouseWheel>", _scroll,    add="+")
            scrollable_frame._parent_canvas.bind("<Button-4>",   _scroll_up, add="+")
            scrollable_frame._parent_canvas.bind("<Button-5>",   _scroll_down, add="+")
        except Exception:
            pass

    # ══════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════

    def _card_title(self, parent, text):
        strip = ctk.CTkFrame(parent, fg_color=DS.G500, height=5, corner_radius=0)
        strip.pack(fill="x")
        ctk.CTkLabel(
            parent, text=text,
            font=_font(40, "bold"),
            text_color=DS.G800
        ).pack(anchor="w", padx=22, pady=(20, 6))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=DIVIDER, height=2).pack(fill="x", padx=22, pady=10)

    def _center_dialog(self, dlg, w, h):
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth()  // 2) - (w // 2)
        y = (dlg.winfo_screenheight() // 2) - (h // 2)
        dlg.geometry(f"{w}x{h}+{x}+{y}")

    # ══════════════════════════════════════════════════════
    # PHONE VALIDATION
    # ══════════════════════════════════════════════════════

    def validate_phone(self, new_value):
        return new_value == "" or (new_value.isdigit() and len(new_value) <= 10)

    # ══════════════════════════════════════════════════════
    # TOAST  — always anchored to root window, fully thread-safe
    # ══════════════════════════════════════════════════════

    def _do_show_toast(self, message, mode="success", duration=3000):
        """Internal — must only be called on the main Tkinter thread."""
        icon  = "✓" if mode == "success" else "✕"
        color = DS.G800 if mode == "success" else DS.RED_D

        # Anchor to the actual root Tk window so the toast is never buried
        root = self.winfo_toplevel()

        toast = ctk.CTkToplevel(root)
        toast.withdraw()
        toast.overrideredirect(True)

        frame = ctk.CTkFrame(toast, fg_color=color, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        ctk.CTkLabel(
            inner, text=icon,
            font=_font(26, "bold"),
            text_color=DS.G200 if mode == "success" else DS.WHITE,
            width=30
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            inner, text=message,
            font=_font(20, "bold"),
            text_color=DS.WHITE, anchor="w"
        ).pack(side="left", fill="x", expand=True)

        toast.update_idletasks()
        sw, sh = toast.winfo_screenwidth(), toast.winfo_screenheight()
        tw, th = 520, 68
        toast.geometry(f"{tw}x{th}+{sw - tw - 20}+20")
        toast.deiconify()
        toast.lift()
        toast.attributes("-topmost", True)
        toast.after(duration, toast.destroy)

    def show_toast(self, message, mode="success", duration=3000):
        """Thread-safe — safe to call from background threads."""
        try:
            self.after(0, lambda: self._do_show_toast(message, mode, duration))
        except Exception:
            pass

    # ══════════════════════════════════════════════════════
    # DELETE CONFIRM MODAL
    # ══════════════════════════════════════════════════════

    def confirm_delete_recipient(self, recipient):
        root = self.winfo_toplevel()
        dlg = ctk.CTkToplevel(root)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(root)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 560, 400)

        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        ctk.CTkFrame(outer, fg_color=DS.RED, height=5, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=28)

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))

        icon_bg = ctk.CTkFrame(hdr, fg_color="#FEE2E2", width=70, height=70, corner_radius=35)
        icon_bg.pack(side="left", padx=(0, 18))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(
            icon_bg, text="?",
            font=_font(38, "bold"), text_color=DS.RED
        ).place(relx=0.5, rely=0.5, anchor="center")

        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(
            title_col, text="Delete Recipient",
            font=_font(28, "bold"), text_color=DS.N800
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_col, text="This action cannot be undone.",
            font=_font(20), text_color=DS.N400
        ).pack(anchor="w")

        preview = ctk.CTkFrame(inner, fg_color=DS.G100, corner_radius=10,
                                border_width=1, border_color=DS.G200)
        preview.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            preview, text=recipient["name"],
            font=_font(26, "bold"), text_color=DS.G800
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            preview, text=recipient["phone"],
            font=_font(24), text_color=DS.N600
        ).pack(anchor="w", padx=18, pady=(0, 14))

        ctk.CTkLabel(
            inner, text="Are you sure you want to delete this recipient?",
            font=_font(22), text_color=DS.N600
        ).pack(anchor="w", pady=(0, 20))

        bf = ctk.CTkFrame(inner, fg_color="transparent")
        bf.pack(fill="x")
        bf.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            bf, text="Keep",
            command=dlg.destroy,
            fg_color=DS.N100, text_color=DS.N800, hover_color=DS.N200,
            height=64, corner_radius=10, font=_font(22)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            bf, text="Delete",
            command=lambda: self.delete_and_close(recipient["phone"], dlg),
            fg_color=DS.RED, hover_color=DS.RED_D, text_color=DS.WHITE,
            height=64, corner_radius=10, font=_font(22, "bold")
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        dlg.lift()
        dlg.attributes("-topmost", True)
        dlg.focus_force()

    def delete_and_close(self, phone, modal):
        delete_recipient(phone)
        modal.destroy()
        self.refresh_recipients()
        self.show_toast("Recipient deleted successfully")

    # ══════════════════════════════════════════════════════
    # WEATHER LOCATION CARD
    # ══════════════════════════════════════════════════════

    def create_weather_card(self):

        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16,
                             border_width=1, border_color=DS.N200)
        card.pack(fill="x", padx=30, pady=(30, 16))

        self._card_title(card, "Weather Location")

        ctk.CTkLabel(
            card,
            text="Set your location in Quezon province to get weather-based forecasts.\n"
                 "Used for weather based spraying decisions.",
            font=_font(26),
            text_color=GRAY,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 14))

        self._divider(card)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(anchor="w", padx=22, pady=(0, 18))

        ctk.CTkLabel(row, text="Municipality:",
                     font=_font(28), text_color=GRAY).grid(row=0, column=0, sticky="w")

        self.muni = ctk.CTkComboBox(
            row,
            values=["Lucban, Quezon", "Lucena City"],
            width=300, height=58,
            font=_font(26),
            dropdown_font=_font(24),
            fg_color=FIELD_BG,
            button_color=DS.G500,
            border_color=DS.G400,
            border_width=2,
            corner_radius=10,
            command=self.update_barangays
        )
        self.muni.grid(row=0, column=1, padx=(14, 34))

        ctk.CTkLabel(row, text="Barangay:",
                     font=_font(28), text_color=GRAY).grid(row=0, column=2, sticky="w")

        self.brgy = ctk.CTkComboBox(
            row,
            values=self.lucban_barangays,
            width=300, height=58,
            font=_font(26),
            dropdown_font=_font(24),
            fg_color=FIELD_BG,
            button_color=DS.G500,
            border_color=DS.G400,
            border_width=2,
            corner_radius=10
        )
        self.brgy.grid(row=0, column=3, padx=(14, 34))

        ctk.CTkButton(
            row,
            text="Save Location",
            fg_color=DS.G500, hover_color=DS.G600,
            width=240, height=58,
            corner_radius=10,
            font=_font(26, "bold"),
            text_color=DS.WHITE,
            command=self.save_location
        ).grid(row=0, column=4)

        self.location_frame = ctk.CTkFrame(card, fg_color=DS.G100, corner_radius=10,
                                            border_width=1, border_color=DS.G200)
        self.location_frame.pack(anchor="w", padx=22, pady=(6, 22))

        self.location_label = ctk.CTkLabel(
            self.location_frame,
            text="Location Set: None",
            font=_font(26),
            text_color=DS.G800,
            padx=18, pady=10
        )
        self.location_label.pack()

        self._load_saved_location_into_ui()

    def _load_saved_location_into_ui(self):
        try:
            loc = get_location()
            muni = loc.get("municipality", "")
            brgy = loc.get("barangay", "")
            if muni:
                self.muni.set(muni)
                self.update_barangays(muni)
            if brgy:
                self.brgy.set(brgy)
            if muni and brgy:
                self.location_label.configure(
                    text=f"Location Set: {brgy}, {muni}"
                )
        except Exception as e:
            print(f"Could not load saved location: {e}")

    def update_barangays(self, value):
        if "Lucena" in value:
            self.brgy.configure(values=self.lucena_barangays)
            self.brgy.set(self.lucena_barangays[0])
        else:
            self.brgy.configure(values=self.lucban_barangays)
            self.brgy.set(self.lucban_barangays[0])

    def save_location(self):
        if not self.muni.get() or not self.brgy.get():
            self.show_toast("Failed to save location — please try again", mode="error")
            return
        save_location(self.brgy.get(), self.muni.get())
        self.location_label.configure(
            text=f"Location Set: {self.brgy.get()}, {self.muni.get()}"
        )
        try:
            from core.weather_service import get_weather_service
            get_weather_service().reload_location()
        except Exception as e:
            print(f"Could not reload weather service after location save: {e}")
        self.show_toast("Weather location saved successfully")

    # ══════════════════════════════════════════════════════
    # SMS RECIPIENTS CARD
    # ══════════════════════════════════════════════════════

    def create_sms_card(self):

        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16,
                             border_width=1, border_color=DS.N200)
        card.pack(fill="x", padx=30, pady=(0, 30))

        self._card_title(card, "SMS Recipients")

        try:
            from core.session import get_phone
            saved_phone = get_phone()
        except Exception:
            saved_phone = None

        if saved_phone:
            reg_frame = ctk.CTkFrame(card, fg_color=DS.G100, corner_radius=10,
                                      border_width=1, border_color=DS.G200)
            reg_frame.pack(fill="x", padx=22, pady=(0, 12))

            ctk.CTkLabel(reg_frame,
                         text="Registered number from setup:",
                         font=_font(24), text_color=DS.N600
                         ).pack(side="left", padx=(18, 10), pady=12)

            ctk.CTkLabel(reg_frame,
                         text=saved_phone,
                         font=_font(26, "bold"), text_color=DS.G800
                         ).pack(side="left", pady=12)

        self._divider(card)

        add_frame = ctk.CTkFrame(card, fg_color=DS.G50, corner_radius=12,
                                  border_width=1, border_color=DS.N200)
        add_frame.pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkLabel(add_frame, text="Add Recipient",
                     font=_font(30, "bold"), text_color=DS.G800
                     ).pack(anchor="w", padx=18, pady=(16, 12))

        phone_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        phone_row.pack(anchor="w", padx=18, pady=(0, 10))

        ctk.CTkLabel(phone_row, text="Mobile Number:",
                     font=_font(28), text_color=GRAY).grid(row=0, column=0, sticky="w")

        prefix = ctk.CTkEntry(
            phone_row, width=90, justify="center",
            fg_color=FIELD_BG, corner_radius=8,
            border_color=DS.G400, border_width=2,
            font=_font(26), height=58
        )
        prefix.grid(row=0, column=1, padx=(14, 0))
        prefix.insert(0, "+63")
        prefix.configure(state="disabled")

        vcmd = (self.register(self.validate_phone), "%P")

        self.phone_entry = ctk.CTkEntry(
            phone_row, width=320, height=58,
            corner_radius=8,
            border_color=DS.G400, border_width=2,
            font=_font(26),
            validate="key", validatecommand=vcmd,
            placeholder_text="9XXXXXXXXX"
        )
        self.phone_entry.grid(row=0, column=2, padx=(8, 0))

        name_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        name_row.pack(anchor="w", padx=18, pady=(0, 18))

        ctk.CTkLabel(name_row, text="Name:",
                     font=_font(28), text_color=GRAY).grid(row=0, column=0, sticky="w")

        self.name_entry = ctk.CTkEntry(
            name_row, width=410, height=58,
            corner_radius=8,
            border_color=DS.G400, border_width=2,
            font=_font(26),
            placeholder_text="Optional"
        )
        self.name_entry.grid(row=0, column=1, padx=(14, 0))

        ctk.CTkButton(
            name_row, text="Add",
            fg_color=DS.G500, hover_color=DS.G600,
            text_color=DS.WHITE,
            width=150, height=58,
            corner_radius=10,
            font=_font(26, "bold"),
            command=self.add_recipient
        ).grid(row=0, column=2, padx=(14, 0))

        ctk.CTkLabel(card, text="Recipients",
                     font=_font(30, "bold"), text_color=DS.G800
                     ).pack(anchor="w", padx=22, pady=(0, 8))

        self.recipients_container = ctk.CTkFrame(card, fg_color=DS.G50, corner_radius=12,
                                                   border_width=1, border_color=DS.N200)
        self.recipients_container.pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkButton(
            card, text="Save Recipients",
            fg_color=DS.G500, hover_color=DS.G600,
            text_color=DS.WHITE,
            width=320, height=62,
            corner_radius=10,
            font=_font(28, "bold"),
            command=self.sync_recipients
        ).pack(pady=(0, 24))

        self.refresh_recipients()

    def add_recipient(self):
        phone = self.phone_entry.get().strip()
        name  = self.name_entry.get().strip()

        if not phone.isdigit() or len(phone) != 10:
            self.show_toast("Invalid mobile number — enter exactly 10 digits", mode="error")
            return

        add_recipient("+63" + phone, name if name else phone)
        self.phone_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.refresh_recipients()
        self.show_toast("Recipient added successfully")

    def sync_recipients(self):
        if self.hardware:
            phones = [r["phone"] for r in get_recipients()]
            self.hardware.sync_recipients_bulk(phones)
            self.show_toast("Recipients synced to controller")

    def refresh_recipients(self):
        for w in self.recipients_container.winfo_children():
            w.destroy()

        recipients = get_recipients()

        if not recipients:
            ctk.CTkLabel(
                self.recipients_container,
                text="No recipients added yet.",
                font=_font(28), text_color=DS.N400
            ).pack(pady=24)
            return

        for r in recipients:
            row_card = ctk.CTkFrame(
                self.recipients_container,
                fg_color=DS.WHITE, corner_radius=14,
                border_width=1, border_color=DS.N200
            )
            row_card.pack(fill="x", padx=10, pady=6)

            strip = ctk.CTkFrame(row_card, fg_color=DS.G500, corner_radius=10, height=4)
            strip.pack(fill="x", padx=3, pady=(3, 0))

            body = ctk.CTkFrame(row_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=12)

            avatar = ctk.CTkFrame(body, fg_color=DS.G100,
                                   corner_radius=999, width=58, height=58)
            avatar.pack_propagate(False)
            avatar.pack(side="left", padx=(0, 14))
            ctk.CTkLabel(avatar, text=" ", font=_font(28)).pack(expand=True)

            info = ctk.CTkFrame(body, fg_color="transparent")
            info.pack(side="left", expand=True, anchor="nw")

            ctk.CTkLabel(info, text=r["name"],
                         font=_font(28, "bold"), text_color=DS.G800,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=r["phone"],
                         font=_font(24), text_color=DS.N600,
                         anchor="w").pack(anchor="w")

            ctk.CTkButton(
                body, text="Delete",
                fg_color=DS.RED, hover_color=DS.RED_D,
                text_color=DS.WHITE,
                width=150, height=54,
                corner_radius=10,
                font=_font(24, "bold"),
                command=lambda rec=r: self.confirm_delete_recipient(rec)
            ).pack(side="right")

    # ══════════════════════════════════════════════════════
    # WIFI CONFIGURATION CARD
    # ══════════════════════════════════════════════════════

    def _wifi_nmcli_available(self):
        return shutil.which("nmcli") is not None

    def _wifi_scan(self):
        """Scan for SSIDs via nmcli — safe to call from background thread."""
        try:
            result = subprocess.run(
                ["nmcli", "--terse", "--fields", "SSID,SIGNAL",
                 "device", "wifi", "list", "--rescan", "yes"],
                capture_output=True, text=True, timeout=15
            )
            seen = {}
            for line in result.stdout.splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    try:
                        signal = int(parts[-1].strip())
                    except ValueError:
                        signal = 0
                    if ssid and ssid not in seen:
                        seen[ssid] = signal
            return [s for s, _ in sorted(seen.items(), key=lambda x: x[1], reverse=True)]
        except Exception:
            return []

    def _wifi_current_ssid(self):
        """Return (ssid, signal_str) of active WiFi, or (None, None)."""
        try:
            result = subprocess.run(
                ["nmcli", "--terse", "--fields",
                 "TYPE,NAME,DEVICE,STATE", "connection", "show", "--active"],
                capture_output=True, text=True, timeout=8
            )
            for line in result.stdout.splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 4 and parts[0].strip().lower() in ("wifi", "802-11-wireless"):
                    name   = parts[1].strip()
                    device = parts[2].strip()
                    state  = parts[3].strip()
                    if state.lower() == "activated" and name:
                        try:
                            sig_result = subprocess.run(
                                ["nmcli", "--terse", "--fields",
                                 "SSID,SIGNAL", "device", "wifi",
                                 "list", "ifname", device],
                                capture_output=True, text=True, timeout=8
                            )
                            for sig_line in sig_result.stdout.splitlines():
                                sp = sig_line.strip().split(":")
                                if len(sp) >= 2 and sp[0].strip() == name:
                                    return name, f"{sp[-1].strip()}%"
                        except Exception:
                            pass
                        return name, None
            return None, None
        except Exception:
            return None, None

    def _wifi_connect(self, ssid, password):
        """
        Connect to the given SSID using nmcli.
        Returns (success: bool, message: str).
        Never logs the plain-text password.
        """
        if not ssid:
            return False, "No SSID selected."
        try:
            # First try activating an existing saved profile (no password needed)
            activate = subprocess.run(
                ["nmcli", "connection", "up", ssid],
                capture_output=True, text=True, timeout=30
            )
            if activate.returncode == 0:
                return True, f"Connected to {ssid}."

            # Build connect command with password
            args = ["nmcli", "device", "wifi", "connect", ssid]
            if password:
                args += ["password", password]

            result = subprocess.run(
                args, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return True, f"Connected to {ssid}."

            stderr   = result.stderr.lower()
            stdout   = result.stdout.lower()
            combined = stderr + stdout

            if any(k in combined for k in (
                "secrets were required", "no secrets",
                "wrong password", "802-11-wireless-security"
            )):
                return False, "Incorrect password."
            elif any(k in combined for k in ("network not found", "no network")):
                return False, "Network not found."
            elif any(k in combined for k in ("no wifi", "no suitable")):
                return False, "No WiFi adapter detected."
            else:
                safe_msg = result.stderr.strip()
                if password:
                    safe_msg = safe_msg.replace(password, "****")
                return False, f"Connection failed: {safe_msg[:120]}"

        except subprocess.TimeoutExpired:
            return False, "Connection timed out."
        except FileNotFoundError:
            return False, "nmcli not found. Install NetworkManager."
        except Exception as exc:
            return False, f"Unexpected error: {exc}"

    def create_wifi_card(self):
        """Build the WiFi Configuration settings card."""

        self._wifi_scanning   = False
        self._wifi_connecting = False

        card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=16,
            border_width=1, border_color=DS.N200
        )
        card.pack(fill="x", padx=30, pady=(0, 30))

        self._card_title(card, "WiFi Configuration")

        ctk.CTkLabel(
            card,
            text="Scan and connect to an available WiFi network.\n"
                 "Uses NetworkManager (nmcli) — safe for existing connections.",
            font=_font(26),
            text_color=GRAY,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 10))

        self._divider(card)

        # ── Current connection status
        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=22, pady=(0, 14))

        ctk.CTkLabel(
            status_row, text="Current WiFi:",
            font=_font(28, "bold"), text_color=DS.G800
        ).pack(side="left")

        self._wifi_current_label = ctk.CTkLabel(
            status_row, text="Checking…",
            font=_font(26), text_color=DS.N400
        )
        self._wifi_current_label.pack(side="left", padx=(12, 0))

        self._wifi_signal_badge = ctk.CTkLabel(
            status_row, text="",
            fg_color=DS.G100, corner_radius=8,
            text_color=DS.G800, font=_font(22, "bold"),
            padx=12, pady=4
        )
        self._wifi_signal_badge.pack(side="left", padx=(10, 0))

        self._divider(card)

        # ── SSID row
        ssid_row = ctk.CTkFrame(card, fg_color="transparent")
        ssid_row.pack(fill="x", padx=22, pady=(0, 12))

        ctk.CTkLabel(
            ssid_row, text="Network (SSID):",
            font=_font(28), text_color=GRAY
        ).pack(side="left")

        self._wifi_ssid_var  = ctk.StringVar(value="")
        self._wifi_ssid_menu = ctk.CTkComboBox(
            ssid_row,
            variable=self._wifi_ssid_var,
            values=["Click \"Scan\" to load networks"],
            width=400, height=58,
            font=_font(26), dropdown_font=_font(24),
            fg_color=FIELD_BG, button_color=DS.G500,
            border_color=DS.G400, border_width=2,
            corner_radius=10, state="readonly"
        )
        self._wifi_ssid_menu.pack(side="left", padx=(14, 14))

        self._wifi_scan_btn = ctk.CTkButton(
            ssid_row, text="⟳  Scan",
            fg_color=DS.N100, hover_color=DS.N200,
            text_color=DS.N800,
            width=160, height=58, corner_radius=10,
            font=_font(26, "bold"),
            command=self._on_wifi_scan
        )
        self._wifi_scan_btn.pack(side="left")

        # ── Password row
        pw_row = ctk.CTkFrame(card, fg_color="transparent")
        pw_row.pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkLabel(
            pw_row, text="Password:",
            font=_font(28), text_color=GRAY
        ).pack(side="left")

        self._wifi_pw_entry = ctk.CTkEntry(
            pw_row,
            width=400, height=58,
            corner_radius=10,
            border_color=DS.G400, border_width=2,
            font=_font(26), show="●",
            placeholder_text="Enter WiFi password"
        )
        self._wifi_pw_entry.pack(side="left", padx=(14, 14))

        self._wifi_pw_visible = False
        self._wifi_pw_toggle  = ctk.CTkButton(
            pw_row, text="Show",
            fg_color=DS.N100, hover_color=DS.N200,
            text_color=DS.N800,
            width=120, height=58, corner_radius=10,
            font=_font(24),
            command=self._toggle_wifi_pw_visibility
        )
        self._wifi_pw_toggle.pack(side="left")

        # ── Connect button + status
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.pack(fill="x", padx=22, pady=(0, 18))

        self._wifi_connect_btn = ctk.CTkButton(
            action_row, text="Connect",
            fg_color=DS.G500, hover_color=DS.G600,
            text_color=DS.WHITE,
            width=220, height=62, corner_radius=10,
            font=_font(28, "bold"),
            command=self._on_wifi_connect
        )
        self._wifi_connect_btn.pack(side="left")

        self._wifi_op_label = ctk.CTkLabel(
            action_row, text="",
            font=_font(24), text_color=DS.N400
        )
        self._wifi_op_label.pack(side="left", padx=(18, 0))

        # ── nmcli unavailable notice
        if not self._wifi_nmcli_available():
            notice = ctk.CTkFrame(
                card, fg_color="#FFF8E1",
                corner_radius=10, border_width=1, border_color="#FFE082"
            )
            notice.pack(fill="x", padx=22, pady=(0, 16))
            ctk.CTkLabel(
                notice,
                text="⚠  nmcli (NetworkManager) not detected. "
                     "WiFi management may not be available on this system.",
                font=_font(22), text_color="#795548"
            ).pack(anchor="w", padx=16, pady=10)

        # Kick off silent initial status refresh
        threading.Thread(target=self._wifi_refresh_current_status, daemon=True).start()

    # ── WiFi helpers ──────────────────────────────────────

    def _toggle_wifi_pw_visibility(self):
        self._wifi_pw_visible = not self._wifi_pw_visible
        self._wifi_pw_entry.configure(show="" if self._wifi_pw_visible else "●")
        self._wifi_pw_toggle.configure(text="Hide" if self._wifi_pw_visible else "Show")

    def _wifi_refresh_current_status(self):
        """Background thread: fetch current SSID and update labels via after()."""
        ssid, signal = self._wifi_current_ssid()
        try:
            if ssid:
                badge = f"📶 {signal}" if signal else "📶 Connected"
                self.after(0, lambda: self._wifi_current_label.configure(
                    text=ssid, text_color=DS.G800))
                self.after(0, lambda: self._wifi_signal_badge.configure(text=badge))
            else:
                self.after(0, lambda: self._wifi_current_label.configure(
                    text="Not connected", text_color=DS.N400))
                self.after(0, lambda: self._wifi_signal_badge.configure(text=""))
        except Exception:
            pass

    def _on_wifi_scan(self):
        if self._wifi_scanning:
            return
        self._wifi_scanning = True
        self._wifi_scan_btn.configure(state="disabled", text="Scanning…")
        self._wifi_op_label.configure(text="Scanning for networks…", text_color=DS.N400)
        threading.Thread(target=self._wifi_scan_bg, daemon=True).start()

    def _wifi_scan_bg(self):
        try:
            ssids = self._wifi_scan()
        finally:
            self._wifi_scanning = False
        try:
            if ssids:
                self.after(0, lambda: self._wifi_ssid_menu.configure(values=ssids))
                self.after(0, lambda: self._wifi_ssid_menu.set(ssids[0]))
                msg = f"{len(ssids)} network(s) found."
                self.after(0, lambda: self._wifi_op_label.configure(
                    text=msg, text_color=DS.G800))
            else:
                self.after(0, lambda: self._wifi_ssid_menu.configure(
                    values=["No networks found — try again"]))
                self.after(0, lambda: self._wifi_ssid_menu.set(
                    "No networks found — try again"))
                self.after(0, lambda: self._wifi_op_label.configure(
                    text="No networks found.", text_color=DS.AMBER))
            self.after(0, lambda: self._wifi_scan_btn.configure(
                state="normal", text="⟳  Scan"))
        except Exception:
            pass

    def _on_wifi_connect(self):
        if self._wifi_connecting:
            return

        ssid = self._wifi_ssid_var.get().strip()
        if not ssid or "Click" in ssid or "No networks" in ssid:
            self._wifi_op_label.configure(
                text="Please select a network first.", text_color=DS.AMBER)
            return

        # Snapshot the password BEFORE clearing the entry
        pw_snapshot = self._wifi_pw_entry.get()

        self._wifi_connecting = True
        self._wifi_connect_btn.configure(state="disabled")
        self._wifi_op_label.configure(
            text=f"Connecting to {ssid}…", text_color=DS.N400)

        # Clear entry and reset show/hide state immediately on the UI thread
        self._wifi_pw_entry.delete(0, "end")
        self._wifi_pw_visible = False
        self._wifi_pw_entry.configure(show="●")
        self._wifi_pw_toggle.configure(text="Show")

        # Hand off the snapshot (not the entry widget) to the background thread
        threading.Thread(
            target=self._wifi_connect_bg,
            args=(ssid, pw_snapshot),
            daemon=True
        ).start()

    def _wifi_connect_bg(self, ssid, password):
        """Background: attempt connection, then update UI on main thread."""
        success, message = self._wifi_connect(ssid, password)
        password = None  # overwrite as soon as no longer needed  # noqa: F841

        self._wifi_connecting = False

        try:
            self.after(0, lambda: self._wifi_connect_btn.configure(state="normal"))

            if success:
                self.after(0, lambda: self._wifi_op_label.configure(
                    text=f"✓  {message}", text_color=DS.G800))
                threading.Thread(
                    target=self._wifi_refresh_current_status, daemon=True).start()
                self.show_toast(f"Connected to {ssid} successfully")
            else:
                self.after(0, lambda: self._wifi_op_label.configure(
                    text=f"✕  {message}", text_color=DS.RED))
                self.show_toast(message, mode="error")
        except Exception:
            pass

    # ══════════════════════════════════════════════════════
    # ESP32 CONNECTION CARD
    # ══════════════════════════════════════════════════════

    def create_esp32_card(self):
        """Build the ESP32 Controller Connection settings card."""

        self._esp_scanning   = False
        self._esp_connecting = False

        self._esp_conn: ESP32Connection | None = getattr(self.hardware, "_conn", None)

        card = ctk.CTkFrame(
            self, fg_color=DS.WHITE, corner_radius=16,
            border_width=1, border_color=DS.N200
        )
        card.pack(fill="x", padx=30, pady=(0, 30))

        self._card_title(card, "ESP32 Controller")

        ctk.CTkLabel(
            card,
            text="Manage the USB serial connection to the ESP32 hardware controller.\n"
                 "The app will auto-detect and reconnect when the device is plugged in.",
            font=_font(26), text_color=GRAY, justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 10))

        self._divider(card)

        # ── Status badge row
        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=22, pady=(0, 14))

        ctk.CTkLabel(
            status_row, text="Status:",
            font=_font(28, "bold"), text_color=DS.G800
        ).pack(side="left")

        self._esp_status_badge = ctk.CTkLabel(
            status_row, text="  Checking…  ",
            fg_color=DS.N200, corner_radius=8,
            text_color=DS.N600, font=_font(22, "bold"),
            padx=14, pady=5
        )
        self._esp_status_badge.pack(side="left", padx=(12, 0))

        self._esp_port_label = ctk.CTkLabel(
            status_row, text="", font=_font(22), text_color=DS.N400)
        self._esp_port_label.pack(side="left", padx=(10, 0))

        self._esp_hint_label = ctk.CTkLabel(
            status_row, text="", font=_font(20), text_color=DS.AMBER)
        self._esp_hint_label.pack(side="left", padx=(16, 0))

        self._divider(card)

        # ── Port selector row
        port_row = ctk.CTkFrame(card, fg_color="transparent")
        port_row.pack(fill="x", padx=22, pady=(0, 12))

        ctk.CTkLabel(
            port_row, text="USB Port:",
            font=_font(28), text_color=GRAY
        ).pack(side="left")

        self._esp_port_var  = ctk.StringVar(value="")
        self._esp_port_menu = ctk.CTkComboBox(
            port_row,
            variable=self._esp_port_var,
            values=["Click \"Scan\" to refresh ports"],
            width=380, height=58,
            font=_font(26), dropdown_font=_font(24),
            fg_color=FIELD_BG, button_color=DS.G500,
            border_color=DS.G400, border_width=2,
            corner_radius=10, state="readonly"
        )
        self._esp_port_menu.pack(side="left", padx=(14, 14))

        self._esp_scan_btn = ctk.CTkButton(
            port_row, text="⟳  Scan",
            fg_color=DS.N100, hover_color=DS.N200,
            text_color=DS.N800,
            width=160, height=58, corner_radius=10,
            font=_font(26, "bold"),
            command=self._on_esp_scan
        )
        self._esp_scan_btn.pack(side="left")

        # ── Action buttons row
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.pack(fill="x", padx=22, pady=(0, 14))

        self._esp_connect_btn = ctk.CTkButton(
            action_row, text="Connect",
            fg_color=DS.G500, hover_color=DS.G600,
            text_color=DS.WHITE,
            width=200, height=62, corner_radius=10,
            font=_font(28, "bold"),
            command=self._on_esp_connect
        )
        self._esp_connect_btn.pack(side="left", padx=(0, 10))

        self._esp_disconnect_btn = ctk.CTkButton(
            action_row, text="Disconnect",
            fg_color=DS.N100, hover_color=DS.N200,
            text_color=DS.N800,
            width=200, height=62, corner_radius=10,
            font=_font(28, "bold"),
            command=self._on_esp_disconnect
        )
        self._esp_disconnect_btn.pack(side="left", padx=(0, 18))

        self._esp_op_label = ctk.CTkLabel(
            action_row, text="", font=_font(24), text_color=DS.N400)
        self._esp_op_label.pack(side="left")

        if self._esp_conn:
            self._esp_conn._on_status_change = self._esp_status_callback

        self.after(200, lambda: threading.Thread(
            target=self._esp_initial_refresh, daemon=True).start())

    # ── ESP32 helpers ─────────────────────────────────────────────────────────

    def _esp_initial_refresh(self):
        allowed = self._esp_conn.ALLOWED_PORTS if self._esp_conn else None
        ports   = _list_serial_ports(allowed)
        try:
            self._esp_update_port_menu(ports)
            if self._esp_conn:
                self._esp_status_callback(
                    self._esp_conn.state, self._esp_conn.port, "")
        except Exception:
            pass

    def _esp_status_callback(self, state: str, port, message: str):
        color_map = {
            STATE_CONNECTED:    (DS.G100,    DS.G800),
            STATE_DISCONNECTED: (DS.N200,    DS.N600),
            STATE_ERROR:        ("#FEE2E2",  DS.RED),
            STATE_CONNECTING:   ("#FFF8E1",  "#795548"),
        }
        bg, fg = color_map.get(state, (DS.N200, DS.N600))

        def _update():
            try:
                self._esp_status_badge.configure(
                    text=f"  {state}  ", fg_color=bg, text_color=fg)
                self._esp_port_label.configure(
                    text=f"({port})" if port else "")
                if state == STATE_CONNECTED:
                    self._esp_hint_label.configure(text="")
                    self._esp_op_label.configure(
                        text=f"✓  Connected to {port}.", text_color=DS.G800)
                elif state == STATE_CONNECTING:
                    self._esp_hint_label.configure(text="")
                    self._esp_op_label.configure(
                        text=message or "Connecting…", text_color=DS.N400)
                elif state == STATE_ERROR:
                    self._esp_hint_label.configure(
                        text="Tap Connect to retry.", text_color=DS.AMBER)
                    self._esp_op_label.configure(
                        text=f"✕  {message}" if message else "✕  Connection error.",
                        text_color=DS.RED)
                else:
                    self._esp_hint_label.configure(
                        text="Select a port and tap Connect.", text_color=DS.N400)
                    self._esp_op_label.configure(text="", text_color=DS.N400)
            except Exception:
                pass

        try:
            self.after(0, _update)
        except Exception:
            pass

    def _esp_update_port_menu(self, ports: list[str]):
        def _do():
            try:
                if ports:
                    self._esp_port_menu.configure(values=ports)
                    pref = self._esp_conn.LAST_CONNECTED_PORT if self._esp_conn else None
                    self._esp_port_menu.set(
                        pref if (pref and pref in ports) else ports[0])
                else:
                    self._esp_port_menu.configure(values=["No ports found — plug in ESP32"])
                    self._esp_port_menu.set("No ports found — plug in ESP32")
            except Exception:
                pass
        try:
            self.after(0, _do)
        except Exception:
            pass

    def _on_esp_scan(self):
        if self._esp_scanning:
            return
        self._esp_scanning = True
        self._esp_scan_btn.configure(state="disabled", text="Scanning…")
        threading.Thread(target=self._esp_scan_bg, daemon=True).start()

    def _esp_scan_bg(self):
        try:
            allowed = self._esp_conn.ALLOWED_PORTS if self._esp_conn else None
            ports   = _list_serial_ports(allowed)
        finally:
            self._esp_scanning = False
        try:
            self.after(0, lambda: self._esp_scan_btn.configure(
                state="normal", text="⟳  Scan"))
            self._esp_update_port_menu(ports)
            count = len(ports)
            msg = f"{count} port(s) found." if count else "No ports found."
            self.after(0, lambda: self._esp_op_label.configure(
                text=msg, text_color=DS.G800 if count else DS.AMBER))
        except Exception:
            pass

    def _on_esp_connect(self):
        if self._esp_connecting or not self._esp_conn:
            return
        port = self._esp_port_var.get().strip()
        if not port or "No ports" in port or "Click" in port:
            self._esp_op_label.configure(
                text="Please select a valid port first.", text_color=DS.AMBER)
            return
        self._esp_connecting = True
        self._esp_connect_btn.configure(state="disabled")
        self._esp_op_label.configure(
            text=f"Connecting to {port}…", text_color=DS.N400)
        threading.Thread(
            target=self._esp_connect_bg, args=(port,), daemon=True).start()

    def _esp_connect_bg(self, port: str):
        ok = self._esp_conn.connect(port)
        try:
            self._esp_connecting = False
            self.after(0, lambda: self._esp_connect_btn.configure(state="normal"))
            if ok:
                self.show_toast(f"Connected to ESP32 on {port}")
            else:
                self.show_toast(f"Could not connect to {port}", mode="error")
        except Exception:
            pass

    def _on_esp_disconnect(self):
        if not self._esp_conn:
            return
        self._esp_conn.disconnect()
        self._esp_op_label.configure(text="Disconnected.", text_color=DS.N600)
        self.show_toast("ESP32 disconnected")


# ══════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.geometry("1200x800")
    root.title("Automated Sprayer System")

    SettingsFrame(root)
    root.mainloop()
