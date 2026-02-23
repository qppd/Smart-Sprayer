import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import customtkinter as ctk

# ---------------------------------------------------------
# PATH
# ---------------------------------------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ---------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------
class D:
    # Greens
    G900 = "#1B3A22"
    G800 = "#1B5E20"
    G700 = "#2E7D32"
    G500 = "#4CAF50"
    G400 = "#66BB6A"
    G200 = "#C8E6C9"
    G100 = "#E8F5E9"
    G50  = "#F1F8F2"

    # Background layers
    BG       = "#D8EAD9"
    CARD     = "#FFFFFF"
    FIELD    = "#EEF5EF"
    FIELD2   = "#E4EFE5"

    # Text
    T_DARK   = "#1B3022"
    T_MID    = "#3A5C40"
    T_LIGHT  = "#6B8F70"
    T_WHITE  = "#FFFFFF"

    # Accents
    RED      = "#EF4444"
    RED_D    = "#DC2626"

    # Sizes
    PILL_W   = 400
    PILL_H   = 52
    ENTRY_H  = 40
    BTN_H    = 52
    RADIUS   = 14


def F(size, weight="normal"):
    w = "bold" if weight == "bold" else "normal"
    return ctk.CTkFont(family="Segoe UI", size=size, weight=w)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def _center(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")


def _divider(parent, color=None):
    ctk.CTkFrame(
        parent, height=1,
        fg_color=color or D.G200,
        corner_radius=0
    ).pack(fill="x", padx=0, pady=0)


def _green_btn(parent, text, cmd, width=None, height=None):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        width=width or D.PILL_W,
        height=height or D.BTN_H,
        corner_radius=D.RADIUS,
        fg_color=D.G700,
        hover_color=D.G800,
        font=F(16, "bold"),
        text_color=D.T_WHITE
    )


def _pill_entry(parent, placeholder, show=None, width=None):
    frame = ctk.CTkFrame(
        parent,
        fg_color=D.FIELD,
        corner_radius=D.RADIUS,
        width=width or D.PILL_W,
        height=D.PILL_H,
        border_width=2,
        border_color=D.G200
    )
    frame.pack_propagate(False)
    entry = ctk.CTkEntry(
        frame,
        placeholder_text=placeholder,
        width=(width or D.PILL_W) - 32,
        height=D.ENTRY_H,
        border_width=0,
        fg_color="transparent",
        text_color=D.T_DARK,
        placeholder_text_color=D.T_LIGHT,
        font=F(15)
    )
    if show:
        entry.configure(show=show)
    entry.place(relx=0.5, rely=0.5, anchor="center")
    return frame, entry



# ---------------------------------------------------------
# LOGO LOADER  (loads once, reused across screens)
# ---------------------------------------------------------
_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

def _make_logo(size):
    """Return a CTkImage of the logo at the given (w,h) size, or None on failure."""
    try:
        img = Image.open(_LOGO_PATH)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


# ---------------------------------------------------------
# CUSTOM MODAL
# ---------------------------------------------------------
def show_error_modal(parent, title, message):
    modal = ctk.CTkToplevel(parent)
    modal.overrideredirect(True)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color=D.CARD)

    w, h = 420, 300
    _center(modal, w, h)

    # Top accent bar
    ctk.CTkFrame(modal, fg_color=D.RED, height=4, corner_radius=0).pack(fill="x")

    container = ctk.CTkFrame(modal, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=30, pady=24)

    # Icon
    icon_bg = ctk.CTkFrame(container, fg_color="#FEE2E2", width=60, height=60, corner_radius=30)
    icon_bg.pack(pady=(0, 16))
    icon_bg.pack_propagate(False)
    ctk.CTkLabel(icon_bg, text="✕", font=F(28, "bold"), text_color=D.RED
                 ).place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text=title, font=F(20, "bold"), text_color=D.T_DARK).pack(pady=(0, 8))
    ctk.CTkLabel(container, text=message, font=F(14), text_color=D.T_MID,
                 wraplength=340, justify="center").pack(pady=(0, 24))

    ctk.CTkButton(
        container, text="OK", width=160, height=44,
        font=F(15, "bold"), fg_color=D.RED, hover_color=D.RED_D,
        corner_radius=10, command=modal.destroy
    ).pack()

    modal.wait_window()


# ---------------------------------------------------------
# PHASE 1 : SPLASH
# ---------------------------------------------------------
def show_splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)

    w, h = 560, 420
    _center(splash, w, h)
    splash.configure(fg_color=D.G800)

    # Logo
    _splash_logo = _make_logo((200, 200))
    if _splash_logo:
        ctk.CTkLabel(splash, image=_splash_logo, text="", fg_color=D.G800
                     ).place(relx=0.5, rely=0.38, anchor="center")
    else:
        ctk.CTkFrame(splash, width=220, height=220, corner_radius=110,
                     fg_color=D.G700).place(relx=0.5, rely=0.38, anchor="center")

    ctk.CTkLabel(
        splash,
        text="AUTOMATED SPRAYER",
        font=F(26, "bold"),
        text_color=D.T_WHITE
    ).place(relx=0.5, rely=0.66, anchor="center")

    ctk.CTkLabel(
        splash,
        text="SYSTEM",
        font=F(26, "bold"),
        text_color=D.G400
    ).place(relx=0.5, rely=0.73, anchor="center")

    # Progress bar
    bar_bg = ctk.CTkFrame(splash, fg_color=D.G700, width=340, height=6, corner_radius=3)
    bar_bg.place(relx=0.5, rely=0.87, anchor="center")

    bar = ctk.CTkFrame(splash, fg_color=D.G400, width=0, height=6, corner_radius=3)
    bar.place(x=(560 - 340) // 2, rely=0.87, anchor="w")

    ctk.CTkLabel(
        splash, text="Initializing system...",
        font=F(12), text_color=D.G400
    ).place(relx=0.5, rely=0.93, anchor="center")

    def animate(p):
        if p <= 1.0:
            bar.configure(width=int(340 * p))
            splash.after(25, lambda: animate(p + 0.02))
        else:
            splash.destroy()

    splash.after(300, lambda: animate(0))
    splash.mainloop()


# ---------------------------------------------------------
# PHASE 2 : WELCOME
# ---------------------------------------------------------
class WelcomeScreen(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.configure(fg_color=D.BG)

        # Left decorative panel
        side = ctk.CTkFrame(self, fg_color=D.G800, width=480, corner_radius=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        _welcome_logo = _make_logo((260, 260))
        if _welcome_logo:
            ctk.CTkLabel(side, image=_welcome_logo, text="", fg_color=D.G800
                         ).place(relx=0.5, rely=0.4, anchor="center")
        else:
            ctk.CTkFrame(side, fg_color=D.G700, width=260, height=260,
                         corner_radius=130).place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            side, text="Farming\nMade Simple",
            font=F(28, "bold"), text_color=D.T_WHITE,
            justify="center"
        ).place(relx=0.5, rely=0.68, anchor="center")

        ctk.CTkLabel(
            side, text="Spraying at your fingertips",
            font=F(14), text_color=D.G400, justify="center"
        ).place(relx=0.5, rely=0.78, anchor="center")

        # Right content
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        box = ctk.CTkFrame(right, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="Welcome", font=F(48, "bold"), text_color=D.T_DARK).pack(pady=(0, 6))
        ctk.CTkLabel(box, text="Automated Sprayer System",
                     font=F(18), text_color=D.T_MID).pack(pady=(0, 50))

        _green_btn(box, "GET STARTED →", self.close, width=340, height=56).pack()

        ctk.CTkLabel(box, text="v1.0  ·  Automated Sprayer System",
                     font=F(11), text_color=D.T_LIGHT).pack(pady=(20, 0))

    def close(self):
        self.destroy()


# ---------------------------------------------------------
# PHASE 3 : LOGIN
# ---------------------------------------------------------
class LoginScreen(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.configure(fg_color=D.BG)
        self._show_pass = False

        # Card
        card = ctk.CTkFrame(self, fg_color=D.CARD, corner_radius=20,
                             border_width=1, border_color=D.G200)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Green top strip
        _strip_canvas_1 = tk.Canvas(card, height=8, bg="#66BB6A", highlightthickness=0)
        _strip_canvas_1.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=48, pady=36)

        # Logo
        _login_logo = _make_logo((90, 90))
        if _login_logo:
            ctk.CTkLabel(inner, image=_login_logo, text="").pack(pady=(0, 20))
        else:
            icon_bg = ctk.CTkFrame(inner, fg_color=D.G100, width=80, height=80, corner_radius=40)
            icon_bg.pack(pady=(0, 20))

        ctk.CTkLabel(inner, text="Sign In", font=F(30, "bold"), text_color=D.T_DARK).pack(pady=(0, 4))
        ctk.CTkLabel(inner,
                     text="Log in using your Sprayer account credentials",
                     font=F(13), text_color=D.T_LIGHT).pack()
        ctk.CTkLabel(inner,
                     text="you may found on the sprayer manual",
                     font=F(13), text_color=D.T_LIGHT).pack(pady=(0, 28))

        # Username
        user_frame, self.user = _pill_entry(inner, "Username")
        user_frame.pack(pady=(0, 10))

        # Password
        pass_outer = ctk.CTkFrame(
            inner, fg_color=D.FIELD, corner_radius=D.RADIUS,
            width=D.PILL_W, height=D.PILL_H,
            border_width=2, border_color=D.G200
        )
        pass_outer.pack(pady=(0, 24))
        pass_outer.pack_propagate(False)

        self.passw = ctk.CTkEntry(
            pass_outer,
            placeholder_text="Password",
            show="•",
            width=D.PILL_W - 80,
            height=D.ENTRY_H,
            border_width=0,
            fg_color="transparent",
            text_color=D.T_DARK,
            placeholder_text_color=D.T_LIGHT,
            font=F(15)
        )
        self.passw.place(x=16, rely=0.5, anchor="w")

        self.eye_btn = ctk.CTkButton(
            pass_outer, text="👁",
            width=40, height=34,
            fg_color=D.G200, hover_color=D.G200,
            text_color=D.T_DARK, font=F(16),
            corner_radius=10, border_width=0,
            command=self._toggle_password
        )
        self.eye_btn.place(relx=1.0, x=-12, rely=0.5, anchor="e")

        _green_btn(inner, "LOG IN", self.login, width=D.PILL_W).pack()

        ctk.CTkLabel(inner, text="You can change your password after login",
                     font=F(12), text_color=D.T_LIGHT).pack(pady=(14, 0))

    def _toggle_password(self):
        self._show_pass = not self._show_pass
        self.passw.configure(show="" if self._show_pass else "•")
        self.eye_btn.configure(text="🙈" if self._show_pass else "👁")

    def login(self):
        if self.user.get() == "sprayer" and self.passw.get() == "1234":
            try:
                from core.session import set_user, update_last_login
                set_user(self.user.get())
                update_last_login()
            except Exception as e:
                print(f"⚠️ Session error: {e}")
            self.destroy()
        else:
            show_error_modal(self, "Login Failed",
                             "Invalid username or password.\nPlease try again.")


# ---------------------------------------------------------
# PHASE 4 : MOBILE NUMBER
# ---------------------------------------------------------
class MobileNumberScreen(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.configure(fg_color=D.BG)

        # Card
        card = ctk.CTkFrame(self, fg_color=D.CARD, corner_radius=20,
                             border_width=1, border_color=D.G200)
        card.place(relx=0.5, rely=0.5, anchor="center")

        _strip_canvas_2 = tk.Canvas(card, height=8, bg="#66BB6A", highlightthickness=0)
        _strip_canvas_2.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=48, pady=36)

        # Logo
        _mobile_logo = _make_logo((90, 90))
        if _mobile_logo:
            ctk.CTkLabel(inner, image=_mobile_logo, text="").pack(pady=(0, 20))
        else:
            icon_bg = ctk.CTkFrame(inner, fg_color=D.G100, width=80, height=80, corner_radius=40)
            icon_bg.pack(pady=(0, 20))

        ctk.CTkLabel(inner, text="Stay Connected",
                     font=F(30, "bold"), text_color=D.T_DARK).pack(pady=(0, 4))
        ctk.CTkLabel(inner, text="Enter your mobile number to receive",
                     font=F(13), text_color=D.T_LIGHT).pack()
        ctk.CTkLabel(inner, text="spray alerts and system notifications",
                     font=F(13), text_color=D.T_LIGHT).pack(pady=(0, 28))

        # Phone row
        phone_outer = ctk.CTkFrame(
            inner, fg_color=D.FIELD, corner_radius=D.RADIUS,
            height=D.PILL_H, border_width=2, border_color=D.G200
        )
        phone_outer.pack(fill="x", pady=(0, 20))
        phone_outer.pack_propagate(False)

        # +63 prefix badge
        prefix = ctk.CTkFrame(phone_outer, fg_color=D.G200, corner_radius=10,
                               width=52, height=36)
        prefix.place(x=8, rely=0.5, anchor="w")
        prefix.pack_propagate(False)
        ctk.CTkLabel(prefix, text="+63", font=F(14, "bold"),
                     text_color=D.G800).place(relx=0.5, rely=0.5, anchor="center")

        self.phone_entry = ctk.CTkEntry(
            phone_outer,
            placeholder_text="9XX XXX XXXX",
            width=D.PILL_W - 90,
            height=D.ENTRY_H,
            border_width=0,
            fg_color="transparent",
            text_color=D.T_DARK,
            placeholder_text_color=D.T_LIGHT,
            font=F(15)
        )
        self.phone_entry.place(x=70, rely=0.5, anchor="w")

        _green_btn(inner, "SUBMIT", self.submit, width=D.PILL_W).pack()

        ctk.CTkLabel(
            inner,
            text="Your number is only used for system alerts.\nWe never share your information.",
            font=F(11), text_color=D.T_LIGHT, justify="center"
        ).pack(pady=(14, 0))

    def submit(self):
        phone = self.phone_entry.get().strip()

        if not phone.isdigit() or len(phone) != 10:
            show_error_modal(self, "Invalid Number",
                             "Please enter a valid 10-digit\nmobile number.")
            return

        full_phone = f"+63{phone}"

        try:
            from core.session import set_phone
            set_phone(full_phone)
        except Exception as e:
            print(f"⚠️ {e}")

        try:
            from core.data_store import add_recipient
            add_recipient(full_phone, "sprayer")
        except Exception as e:
            print(f"⚠️ {e}")

        try:
            from hardware.hardware_interface import get_hardware
            hw = get_hardware()
            if hw and hw.connected:
                hw.send_sms(full_phone,
                    "Welcome to the Automated Sprayer System! "
                    "Your number has been registered. "
                    "You will receive alerts and notifications here.")
        except Exception as e:
            print(f"⚠️ {e}")

        self.destroy()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    show_splash_screen()
    WelcomeScreen().mainloop()
    LoginScreen().mainloop()
    MobileNumberScreen().mainloop()

    try:
        from ui.main_ui import main as ui_main
        ui_main()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()