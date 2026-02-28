# settings.py
# Smart Sprayer Settings Panel (Modernized)

import customtkinter as ctk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_store import get_recipients, add_recipient, delete_recipient, save_location
from hardware.hardware_interface import get_hardware


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
        # Enable mouse-wheel scrolling anywhere in the panel
        self._bind_mousewheel(self)

    # ══════════════════════════════════════════════════════
    # MOUSE-WHEEL SCROLL  (works without touching the scrollbar)
    # ══════════════════════════════════════════════════════

    def _bind_mousewheel(self, scrollable_frame):
        def _scroll(event):
            scrollable_frame._parent_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units"
            )
        def _scroll_up(event):
            scrollable_frame._parent_canvas.yview_scroll(-1, "units")
        def _scroll_down(event):
            scrollable_frame._parent_canvas.yview_scroll(1, "units")

        def _bind_all(widget):
            widget.bind("<MouseWheel>", _scroll,      add="+")
            widget.bind("<Button-4>",   _scroll_up,   add="+")
            widget.bind("<Button-5>",   _scroll_down, add="+")
            for child in widget.winfo_children():
                _bind_all(child)

        _bind_all(scrollable_frame)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: _bind_all(scrollable_frame),
            add="+"
        )

    # ══════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════

    def _card_title(self, parent, text):
        # Accent strip + title — same pattern as scheduling card strip
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
    # TOAST  — matches _show_success_toast in scheduling.py
    # ══════════════════════════════════════════════════════

    def show_toast(self, message, mode="success", duration=3000):
        """Slim bottom-of-screen toast identical in style to scheduling.py."""
        icon  = "✓" if mode == "success" else "✕"
        color = DS.G800 if mode == "success" else DS.RED_D

        toast = ctk.CTkToplevel(self)
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

    # ══════════════════════════════════════════════════════
    # DELETE CONFIRM MODAL — matches _show_cancel_confirmation
    # ══════════════════════════════════════════════════════

    def confirm_delete_recipient(self, recipient):
        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 560, 400)

        # White card with red accent strip — same as scheduling cancel dialog
        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        ctk.CTkFrame(outer, fg_color=DS.RED, height=5, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=28)

        # Header row: icon + title
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

        # Recipient preview card
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

        # Body warning
        ctk.CTkLabel(
            inner, text="Are you sure you want to delete this recipient?",
            font=_font(22), text_color=DS.N600
        ).pack(anchor="w", pady=(0, 20))

        # Buttons — same grid layout as scheduling
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

        # Location status badge
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

        # ── Add recipient section ─────────────────────────
        add_frame = ctk.CTkFrame(card, fg_color=DS.G50, corner_radius=12,
                                  border_width=1, border_color=DS.N200)
        add_frame.pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkLabel(add_frame, text="Add Recipient",
                     font=_font(30, "bold"), text_color=DS.G800
                     ).pack(anchor="w", padx=18, pady=(16, 12))

        # Phone row
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

        # Name row
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

        # ── Recipients list ───────────────────────────────
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
            # Row card — same white card + green strip style as schedule cards
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

            # Avatar circle
            avatar = ctk.CTkFrame(body, fg_color=DS.G100,
                                   corner_radius=999, width=58, height=58)
            avatar.pack_propagate(False)
            avatar.pack(side="left", padx=(0, 14))
            ctk.CTkLabel(avatar, text=" ",
                         font=_font(28)).pack(expand=True)

            # Info — anchor="nw" keeps name/phone top-left aligned
            info = ctk.CTkFrame(body, fg_color="transparent")
            info.pack(side="left", expand=True, anchor="nw")

            ctk.CTkLabel(info, text=r["name"],
                         font=_font(28, "bold"), text_color=DS.G800,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=r["phone"],
                         font=_font(24), text_color=DS.N600,
                         anchor="w").pack(anchor="w")

            # Delete button — same style as Cancel button in scheduling
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
