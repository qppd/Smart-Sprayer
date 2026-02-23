# settings.py
# Smart Sprayer Settings Panel (Modernized)

import customtkinter as ctk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_store import get_recipients, add_recipient, delete_recipient
from hardware.hardware_interface import get_hardware

# ══════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════
BG          = "#eef6f1"
WHITE       = "#ffffff"
GREEN       = "#2e7d32"
BTN_GREEN   = "#43a047"
RED         = "#e53935"
FIELD_BG    = "#dff1e3"
ARROW_GREEN = "#7bc47f"
GRAY        = "#616161"
DIVIDER     = "#e8f5e9"


class SettingsFrame(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.pack(fill="both", expand=True)

        self.hardware = get_hardware()

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

    # ══════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════

    def _card(self, **kwargs):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=18, **kwargs)
        card.pack(fill="x", padx=30, pady=(0, 16))
        return card

    def _card_title(self, parent, text):
        """Section title with accent strip."""
        strip = ctk.CTkFrame(parent, fg_color=GREEN, height=3, corner_radius=0)
        strip.pack(fill="x")

        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=GREEN
        ).pack(anchor="w", padx=22, pady=(16, 4))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=DIVIDER, height=1).pack(fill="x", padx=22, pady=8)

    def _field_label(self, parent, text, col):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=18),
            text_color=GRAY
        ).grid(row=0, column=col, sticky="w")

    # ══════════════════════════════════════════════════════
    # PHONE VALIDATION
    # ══════════════════════════════════════════════════════

    def validate_phone(self, new_value):
        return new_value == "" or (new_value.isdigit() and len(new_value) <= 10)

    # ══════════════════════════════════════════════════════
    # TOAST
    # ══════════════════════════════════════════════════════

    def show_toast(self, title, subtitle="", mode="success"):

        if mode == "success":
            bg_color     = "#1f3d2b"
            circle_color = "#2ecc71"
            icon         = "✓"
            sub_color    = "#cfe8d8"
        else:
            bg_color     = "#5c1f1f"
            circle_color = "#e74c3c"
            icon         = "✕"
            sub_color    = "#f5c6c6"

        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=bg_color)

        width, height = 400, 90
        self.update_idletasks()
        x = self.winfo_screenwidth() - width - 20
        y = 20
        toast.geometry(f"{width}x{height}+{x}+{y}")

        container = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=14)
        container.pack(fill="both", expand=True)

        icon_bg = ctk.CTkFrame(container, width=48, height=48,
                               corner_radius=24, fg_color=circle_color)
        icon_bg.pack_propagate(False)
        icon_bg.pack(side="left", padx=18)

        ctk.CTkLabel(icon_bg, text=icon,
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color="white").pack(expand=True)

        text_frame = ctk.CTkFrame(container, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(text_frame, text=title,
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="white").pack(anchor="w", pady=(20, 0))

        if subtitle:
            ctk.CTkLabel(text_frame, text=subtitle,
                         font=ctk.CTkFont(size=16),
                         text_color=sub_color).pack(anchor="w")

        toast.after(2800, toast.destroy)

    # ══════════════════════════════════════════════════════
    # DELETE CONFIRM MODAL
    # ══════════════════════════════════════════════════════

    def confirm_delete_recipient(self, recipient):

        modal = ctk.CTkToplevel(self)
        modal.overrideredirect(True)
        modal.geometry("480x400")
        modal.grab_set()
        modal.attributes("-topmost", True)

        modal.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  // 2) - 240
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 200
        modal.geometry(f"480x400+{x}+{y}")

        # Outer shadow frame
        outer = ctk.CTkFrame(modal, fg_color="#d0e8d8", corner_radius=20)
        outer.pack(fill="both", expand=True, padx=3, pady=3)

        container = ctk.CTkFrame(outer, fg_color=WHITE, corner_radius=18)
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Warning icon
        icon_frame = ctk.CTkFrame(container, fg_color="#fff8e1",
                                  corner_radius=999, width=64, height=64)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(24, 8))

        ctk.CTkLabel(icon_frame, text="⚠",
                     font=ctk.CTkFont(size=32),
                     text_color="#f39c12").pack(expand=True)

        ctk.CTkLabel(container, text="Delete Recipient",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=GREEN).pack()

        ctk.CTkLabel(container,
                     text="Are you sure you want to delete this recipient?",
                     font=ctk.CTkFont(size=18),
                     text_color=GRAY).pack(pady=(6, 0))

        # Preview card
        preview = ctk.CTkFrame(container, fg_color=FIELD_BG, corner_radius=12)
        preview.pack(fill="x", padx=24, pady=14)

        ctk.CTkLabel(preview,
                     text=f"👤  {recipient['name']}",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=GREEN).pack(anchor="w", padx=18, pady=(12, 2))

        ctk.CTkLabel(preview,
                     text=f"📞  {recipient['phone']}",
                     font=ctk.CTkFont(size=17),
                     text_color=GRAY).pack(anchor="w", padx=18, pady=(0, 12))

        ctk.CTkLabel(container,
                     text="This action cannot be undone.",
                     text_color=RED,
                     font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(0, 14))

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.pack(pady=(0, 20))

        ctk.CTkButton(
            btns, text="Cancel",
            width=160, height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BTN_GREEN,
            hover_color="#388e3c",
            command=modal.destroy
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            btns, text="Delete",
            width=160, height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=RED,
            hover_color="#c62828",
            command=lambda: self.delete_and_close(recipient["phone"], modal)
        ).pack(side="left", padx=12)

    def delete_and_close(self, phone, modal):
        delete_recipient(phone)
        modal.destroy()
        self.refresh_recipients()
        self.show_toast("Recipient deleted", "Number removed", "success")

    # ══════════════════════════════════════════════════════
    # WEATHER LOCATION CARD
    # ══════════════════════════════════════════════════════

    def create_weather_card(self):

        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=18)
        card.pack(fill="x", padx=30, pady=(30, 16))

        self._card_title(card, "🌤  Weather Location")

        ctk.CTkLabel(
            card,
            text="Set your location in Quezon province to get weather-based forecasts.\n"
                 "Used for weather based spraying decisions.",
            font=ctk.CTkFont(size=17),
            text_color=GRAY,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self._divider(card)

        # Fields row
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(anchor="w", padx=22, pady=(0, 14))

        ctk.CTkLabel(row, text="Municipality:",
                     font=ctk.CTkFont(size=18),
                     text_color=GRAY).grid(row=0, column=0, sticky="w")

        self.muni = ctk.CTkComboBox(
            row,
            values=["Lucban, Quezon", "Lucena City"],
            width=190, height=38,
            font=ctk.CTkFont(size=17),
            fg_color=FIELD_BG,
            button_color=ARROW_GREEN,
            corner_radius=10,
            command=self.update_barangays
        )
        self.muni.grid(row=0, column=1, padx=(12, 30))

        ctk.CTkLabel(row, text="Barangay:",
                     font=ctk.CTkFont(size=18),
                     text_color=GRAY).grid(row=0, column=2, sticky="w")

        self.brgy = ctk.CTkComboBox(
            row,
            values=self.lucban_barangays,
            width=190, height=38,
            font=ctk.CTkFont(size=17),
            fg_color=FIELD_BG,
            button_color=ARROW_GREEN,
            corner_radius=10
        )
        self.brgy.grid(row=0, column=3, padx=(12, 30))

        ctk.CTkButton(
            row,
            text="Save Location",
            fg_color=BTN_GREEN,
            hover_color="#388e3c",
            width=160, height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=17, weight="bold"),
            command=self.save_location
        ).grid(row=0, column=4)

        # Location status badge
        self.location_frame = ctk.CTkFrame(card, fg_color=FIELD_BG, corner_radius=10)
        self.location_frame.pack(anchor="w", padx=22, pady=(4, 20))

        self.location_label = ctk.CTkLabel(
            self.location_frame,
            text="📍  Location Set: None",
            font=ctk.CTkFont(size=18),
            text_color=GREEN,
            padx=14, pady=8
        )
        self.location_label.pack()

    def update_barangays(self, value):
        if "Lucena" in value:
            self.brgy.configure(values=self.lucena_barangays)
            self.brgy.set(self.lucena_barangays[0])
        else:
            self.brgy.configure(values=self.lucban_barangays)
            self.brgy.set(self.lucban_barangays[0])

    def save_location(self):
        if not self.muni.get() or not self.brgy.get():
            self.show_toast("Failed to save location", "Please try again later", "error")
            return
        self.location_label.configure(
            text=f"📍  Location Set: {self.brgy.get()}, {self.muni.get()}"
        )
        self.show_toast("Weather location saved",
                        "Location will be used for spraying decisions", "success")

    # ══════════════════════════════════════════════════════
    # SMS RECIPIENTS CARD
    # ══════════════════════════════════════════════════════

    def create_sms_card(self):

        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=18)
        card.pack(fill="x", padx=30, pady=(0, 30))

        self._card_title(card, "📱  SMS Recipients")

        # Registered number banner
        try:
            from core.session import get_phone
            saved_phone = get_phone()
        except Exception:
            saved_phone = None

        if saved_phone:
            reg_frame = ctk.CTkFrame(card, fg_color=FIELD_BG, corner_radius=10)
            reg_frame.pack(fill="x", padx=22, pady=(0, 10))

            ctk.CTkLabel(reg_frame,
                         text="📱  Registered number from setup:",
                         font=ctk.CTkFont(size=16),
                         text_color="#4A5A52").pack(side="left", padx=(16, 8), pady=10)

            ctk.CTkLabel(reg_frame,
                         text=saved_phone,
                         font=ctk.CTkFont(size=17, weight="bold"),
                         text_color=GREEN).pack(side="left", pady=10)

        self._divider(card)

        # ── Add recipient section ─────────────────────────
        add_frame = ctk.CTkFrame(card, fg_color=BG, corner_radius=12)
        add_frame.pack(fill="x", padx=22, pady=(0, 14))

        ctk.CTkLabel(add_frame, text="Add Recipient",
                     font=ctk.CTkFont(size=19, weight="bold"),
                     text_color=GREEN).pack(anchor="w", padx=16, pady=(14, 10))

        # Phone row
        phone_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        phone_row.pack(anchor="w", padx=16, pady=(0, 8))

        ctk.CTkLabel(phone_row, text="Mobile Number:",
                     font=ctk.CTkFont(size=18),
                     text_color=GRAY).grid(row=0, column=0, sticky="w")

        prefix = ctk.CTkEntry(phone_row, width=60, justify="center",
                              fg_color=FIELD_BG, corner_radius=8,
                              font=ctk.CTkFont(size=17), height=38)
        prefix.grid(row=0, column=1, padx=(12, 0))
        prefix.insert(0, "+63")
        prefix.configure(state="disabled")

        vcmd = (self.register(self.validate_phone), "%P")

        self.phone_entry = ctk.CTkEntry(
            phone_row, width=220, height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=17),
            validate="key",
            validatecommand=vcmd,
            placeholder_text="9XXXXXXXXX"
        )
        self.phone_entry.grid(row=0, column=2, padx=(6, 0))

        # Name row
        name_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        name_row.pack(anchor="w", padx=16, pady=(0, 14))

        ctk.CTkLabel(name_row, text="Name:",
                     font=ctk.CTkFont(size=18),
                     text_color=GRAY).grid(row=0, column=0, sticky="w")

        self.name_entry = ctk.CTkEntry(
            name_row, width=290, height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=17),
            placeholder_text="Optional"
        )
        self.name_entry.grid(row=0, column=1, padx=(12, 0))

        ctk.CTkButton(
            name_row, text="+ Add",
            fg_color=BTN_GREEN,
            hover_color="#388e3c",
            width=100, height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=17, weight="bold"),
            command=self.add_recipient
        ).grid(row=0, column=2, padx=(12, 0))

        # ── Recipients list ───────────────────────────────
        ctk.CTkLabel(card, text="Recipients",
                     font=ctk.CTkFont(size=19, weight="bold"),
                     text_color=GREEN).pack(anchor="w", padx=22, pady=(0, 6))

        self.recipients_container = ctk.CTkFrame(card, fg_color=BG, corner_radius=12)
        self.recipients_container.pack(fill="x", padx=22, pady=(0, 14))

        # Save button
        ctk.CTkButton(
            card, text="💾  Save Recipients",
            fg_color=BTN_GREEN,
            hover_color="#388e3c",
            width=240, height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.sync_recipients
        ).pack(pady=(0, 20))

        self.refresh_recipients()

    def add_recipient(self):
        phone = self.phone_entry.get().strip()
        name  = self.name_entry.get().strip()

        if not phone.isdigit() or len(phone) != 10:
            self.show_toast("Invalid mobile number", "Enter exactly 10 digits", "error")
            return

        add_recipient("+63" + phone, name if name else phone)
        self.phone_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.refresh_recipients()
        self.show_toast("Recipient added", "Mobile number stored", "success")

    def sync_recipients(self):
        if self.hardware:
            phones = [r["phone"] for r in get_recipients()]
            self.hardware.sync_recipients_bulk(phones)
            self.show_toast("Recipients synced", "Controller updated", "success")

    def refresh_recipients(self):
        for w in self.recipients_container.winfo_children():
            w.destroy()

        recipients = get_recipients()

        if not recipients:
            ctk.CTkLabel(
                self.recipients_container,
                text="No recipients added yet.",
                font=ctk.CTkFont(size=18),
                text_color=GRAY
            ).pack(pady=20)
            return

        for r in recipients:
            row = ctk.CTkFrame(
                self.recipients_container,
                fg_color=WHITE, corner_radius=10
            )
            row.pack(fill="x", padx=10, pady=5)

            # Avatar circle
            avatar = ctk.CTkFrame(row, fg_color=FIELD_BG,
                                  corner_radius=999, width=40, height=40)
            avatar.pack_propagate(False)
            avatar.pack(side="left", padx=(14, 10), pady=10)

            ctk.CTkLabel(avatar, text="👤",
                         font=ctk.CTkFont(size=20)).pack(expand=True)

            # Info
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=4, pady=10)

            ctk.CTkLabel(info, text=r["name"],
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=GREEN).pack(anchor="w")

            ctk.CTkLabel(info, text=r["phone"],
                         font=ctk.CTkFont(size=16),
                         text_color=GRAY).pack(anchor="w")

            # Delete button
            ctk.CTkButton(
                row, text="Delete",
                fg_color="#ffebee",
                text_color=RED,
                hover_color="#ffcdd2",
                width=90, height=34,
                corner_radius=8,
                font=ctk.CTkFont(size=16, weight="bold"),
                border_width=1,
                border_color="#ffcdd2",
                command=lambda rec=r: self.confirm_delete_recipient(rec)
            ).pack(side="right", padx=14)


# ══════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.geometry("1000x650")
    root.title("Automated Sprayer System")

    SettingsFrame(root)
    root.mainloop()