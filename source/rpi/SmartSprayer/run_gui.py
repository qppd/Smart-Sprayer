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

# Import keyboard utilities (KeyboardManager for standalone windows)
try:
    from ui.keyboard_utils import KeyboardManager
    _KB_AVAILABLE = True
except Exception:
    _KB_AVAILABLE = False

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

    # Sizes — elder-friendly
    PILL_W   = 620       # was 400
    PILL_H   = 90        # was 52
    ENTRY_H  = 70        # was 40
    BTN_H    = 90        # was 52
    RADIUS   = 16


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
        font=F(28, "bold"),
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
        font=F(30)
    )
    if show:
        entry.configure(show=show)
    entry.place(relx=0.5, rely=0.5, anchor="center")
    return frame, entry


# ---------------------------------------------------------
# LOGO LOADER
# ---------------------------------------------------------
_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

def _make_logo(size):
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
    modal.wait_visibility()
    modal.grab_set()
    modal.configure(fg_color=D.CARD)

    w, h = 580, 420
    _center(modal, w, h)

    ctk.CTkFrame(modal, fg_color=D.RED, height=6, corner_radius=0).pack(fill="x")

    container = ctk.CTkFrame(modal, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=36, pady=30)

    icon_bg = ctk.CTkFrame(container, fg_color="#FEE2E2", width=90, height=90, corner_radius=45)
    icon_bg.pack(pady=(0, 20))
    icon_bg.pack_propagate(False)
    ctk.CTkLabel(icon_bg, text="✕", font=F(42, "bold"), text_color=D.RED
                 ).place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text=title, font=F(32, "bold"), text_color=D.T_DARK).pack(pady=(0, 10))
    ctk.CTkLabel(container, text=message, font=F(22), text_color=D.T_MID,
                 wraplength=480, justify="center").pack(pady=(0, 28))

    ctk.CTkButton(
        container, text="OK", width=220, height=64,
        font=F(24, "bold"), fg_color=D.RED, hover_color=D.RED_D,
        corner_radius=12, command=modal.destroy
    ).pack()

    modal.wait_window()


# ---------------------------------------------------------
# PHASE 1 : SPLASH
# ---------------------------------------------------------
def show_splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)
    splash.attributes("-fullscreen", True)
    splash.configure(fg_color=D.G800)

    _splash_logo = _make_logo((240, 240))
    if _splash_logo:
        ctk.CTkLabel(splash, image=_splash_logo, text="", fg_color=D.G800
                     ).place(relx=0.5, rely=0.38, anchor="center")
    else:
        ctk.CTkFrame(splash, width=240, height=240, corner_radius=120,
                     fg_color=D.G700).place(relx=0.5, rely=0.38, anchor="center")

    ctk.CTkLabel(
        splash,
        text="AUTOMATED SPRAYER",
        font=F(40, "bold"),
        text_color=D.T_WHITE
    ).place(relx=0.5, rely=0.66, anchor="center")

    ctk.CTkLabel(
        splash,
        text="SYSTEM",
        font=F(40, "bold"),
        text_color=D.G400
    ).place(relx=0.5, rely=0.74, anchor="center")

    bar_bg = ctk.CTkFrame(splash, fg_color=D.G700, width=400, height=8, corner_radius=4)
    bar_bg.place(relx=0.5, rely=0.88, anchor="center")

    bar = ctk.CTkFrame(splash, fg_color=D.G400, width=0, height=8, corner_radius=4)

    ctk.CTkLabel(
        splash, text="Initializing system...",
        font=F(18), text_color=D.G400
    ).place(relx=0.5, rely=0.94, anchor="center")

    def animate(p):
        if p <= 1.0:
            bar.configure(width=int(400 * p))
            splash.after(25, lambda: animate(p + 0.02))
        else:
            splash.destroy()

    def start_animation():
        bar_x = (splash.winfo_width() - 400) // 2
        bar.place(x=bar_x, rely=0.88, anchor="w")
        animate(0)

    splash.after(300, start_animation)
    splash.mainloop()


# ---------------------------------------------------------
# PHASE 2 : WELCOME
# ---------------------------------------------------------
class WelcomeScreen(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.configure(fg_color=D.BG)

        side = ctk.CTkFrame(self, fg_color=D.G800, width=580, corner_radius=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        _welcome_logo = _make_logo((320, 320))
        if _welcome_logo:
            ctk.CTkLabel(side, image=_welcome_logo, text="", fg_color=D.G800
                         ).place(relx=0.5, rely=0.38, anchor="center")
        else:
            ctk.CTkFrame(side, fg_color=D.G700, width=320, height=320,
                         corner_radius=160).place(relx=0.5, rely=0.38, anchor="center")

        ctk.CTkLabel(
            side, text="Pagsasakang Pinadali\nsa Bawat Wisik",
            font=F(42, "bold"), text_color=D.T_WHITE,
            justify="center"
        ).place(relx=0.5, rely=0.70, anchor="center")

        ctk.CTkLabel(
            side, text="Kontrol sa Wisik, Hawak Mo",
            font=F(24), text_color=D.G400, justify="center"
        ).place(relx=0.5, rely=0.81, anchor="center")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        box = ctk.CTkFrame(right, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="Mabuhay!", font=F(68, "bold"), text_color=D.T_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(box, text="Automated Sprayer System",
                     font=F(28), text_color=D.T_MID).pack(pady=(0, 60))

        _green_btn(box, "GET STARTED →", self.close, width=460, height=80).pack()

        ctk.CTkLabel(box, text="Simulan ang Mas Madaling Pagwisik",
                     font=F(18), text_color=D.T_LIGHT).pack(pady=(24, 0))

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

        card = ctk.CTkFrame(self, fg_color=D.CARD, corner_radius=28,
                             border_width=1, border_color=D.G200)
        card.place(relx=0.5, rely=0.5, anchor="center")

        _strip_canvas_1 = tk.Canvas(card, height=12, bg="#66BB6A", highlightthickness=0)
        _strip_canvas_1.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=80, pady=60)

        _login_logo = _make_logo((150, 150))
        if _login_logo:
            ctk.CTkLabel(inner, image=_login_logo, text="").pack(pady=(0, 28))
        else:
            icon_bg = ctk.CTkFrame(inner, fg_color=D.G100, width=130, height=130, corner_radius=65)
            icon_bg.pack(pady=(0, 28))

        ctk.CTkLabel(inner, text="Sign In",
                     font=F(58, "bold"), text_color=D.T_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(inner,
                     text="Log in using your Sprayer account credentials",
                     font=F(26), text_color=D.T_LIGHT).pack()
        ctk.CTkLabel(inner,
                     text="you may found on the sprayer manual",
                     font=F(26), text_color=D.T_LIGHT).pack(pady=(0, 40))

        # Username field
        user_frame = ctk.CTkFrame(
            inner, fg_color=D.FIELD, corner_radius=D.RADIUS,
            width=620, height=90,
            border_width=2, border_color=D.G200
        )
        user_frame.pack(pady=(0, 16))
        user_frame.pack_propagate(False)
        self.user = ctk.CTkEntry(
            user_frame,
            placeholder_text="Username",
            width=580,
            height=70,
            border_width=0,
            fg_color="transparent",
            text_color=D.T_DARK,
            placeholder_text_color=D.T_LIGHT,
            font=F(30)
        )
        self.user.place(relx=0.5, rely=0.5, anchor="center")


        # Password field
        pass_outer = ctk.CTkFrame(
            inner, fg_color=D.FIELD, corner_radius=D.RADIUS,
            width=620, height=90,
            border_width=2, border_color=D.G200
        )
        pass_outer.pack(pady=(0, 36))
        pass_outer.pack_propagate(False)

        self.passw = ctk.CTkEntry(
            pass_outer,
            placeholder_text="Password",
            show="•",
            width=510,
            height=70,
            border_width=0,
            fg_color="transparent",
            text_color=D.T_DARK,
            placeholder_text_color=D.T_LIGHT,
            font=F(30)
        )
        self.passw.place(x=16, rely=0.5, anchor="w")

        self.eye_btn = ctk.CTkButton(
            pass_outer, text="👁",
            width=70, height=60,
            fg_color=D.G200, hover_color=D.G200,
            text_color=D.T_DARK, font=F(28),
            corner_radius=10, border_width=0,
            command=self._toggle_password
        )
        self.eye_btn.place(relx=1.0, x=-14, rely=0.5, anchor="e")


        ctk.CTkButton(
            inner, text="LOG IN",
            command=self.login,
            width=620, height=90,
            corner_radius=D.RADIUS,
            fg_color=D.G700,
            hover_color=D.G800,
            font=F(36, "bold"),
            text_color=D.T_WHITE
        ).pack()

        ctk.CTkLabel(inner, text="You can change your password after login",
                     font=F(22), text_color=D.T_LIGHT).pack(pady=(22, 0))

        # Attach in-app virtual keyboard to all entry fields in this window
        if _KB_AVAILABLE:
            self._kb = KeyboardManager(self)
            self._kb.bind_all(self)

    def _toggle_password(self):
        self._show_pass = not self._show_pass
        self.passw.configure(show="" if self._show_pass else "•")
        self.eye_btn.configure(text="🙈" if self._show_pass else "👁")

    def login(self):
        username = self.user.get()
        password = self.passw.get()
        # Validate against Firebase RTDB (falls back to local if offline)
        valid = False
        try:
            from core.firebase_service import get_firebase_service
            fb = get_firebase_service()
            rtdb_account = fb.get_account_from_rtdb() if fb.connected else None
            if rtdb_account:
                valid = (
                    username == rtdb_account.get("username", "") and
                    password == rtdb_account.get("password", "")
                )
                if not valid:
                    print("⚠️ RTDB credentials did not match")
            else:
                # Firebase offline — fall back to local credentials
                print("ℹ️ Firebase offline — using local credentials")
                from core.session import get_username, verify_password
                valid = (username == get_username()) and verify_password(password)
        except Exception as e:
            print(f"⚠️ Firebase auth error: {e}")
            try:
                from core.session import get_username, verify_password
                valid = (username == get_username()) and verify_password(password)
            except Exception as e2:
                print(f"⚠️ Session error: {e2}")
                valid = (username == "sprayer" and password == "1234")

        if valid:
            try:
                from core.session import set_user, update_last_login
                set_user(username)
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

        card = ctk.CTkFrame(self, fg_color=D.CARD, corner_radius=28,
                             border_width=1, border_color=D.G200)
        card.place(relx=0.5, rely=0.5, anchor="center")

        _strip_canvas_2 = tk.Canvas(card, height=12, bg="#66BB6A", highlightthickness=0)
        _strip_canvas_2.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=80, pady=60)

        _mobile_logo = _make_logo((150, 150))
        if _mobile_logo:
            ctk.CTkLabel(inner, image=_mobile_logo, text="").pack(pady=(0, 28))
        else:
            icon_bg = ctk.CTkFrame(inner, fg_color=D.G100, width=130, height=130, corner_radius=65)
            icon_bg.pack(pady=(0, 28))

        ctk.CTkLabel(inner, text="Stay Connected",
                     font=F(58, "bold"), text_color=D.T_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="Enter your mobile number to receive",
                     font=F(26), text_color=D.T_LIGHT).pack()
        ctk.CTkLabel(inner, text="spray alerts and system notifications",
                     font=F(26), text_color=D.T_LIGHT).pack(pady=(0, 40))

        # Phone row
        phone_outer = ctk.CTkFrame(
            inner, fg_color=D.FIELD, corner_radius=D.RADIUS,
            width=620, height=90,
            border_width=2, border_color=D.G200
        )
        phone_outer.pack(pady=(0, 30))
        phone_outer.pack_propagate(False)

        prefix = ctk.CTkFrame(phone_outer, fg_color=D.G200, corner_radius=12,
                               width=96, height=66)
        prefix.place(x=12, rely=0.5, anchor="w")
        prefix.pack_propagate(False)
        ctk.CTkLabel(prefix, text="+63", font=F(28, "bold"),
                     text_color=D.G800).place(relx=0.5, rely=0.5, anchor="center")

        self.phone_entry = ctk.CTkEntry(
            phone_outer,
            placeholder_text="9XX XXX XXXX",
            width=480,
            height=70,
            border_width=0,
            fg_color="transparent",
            text_color=D.T_DARK,
            placeholder_text_color=D.T_LIGHT,
            font=F(30)
        )
        self.phone_entry.place(x=122, rely=0.5, anchor="w")

        ctk.CTkButton(
            inner, text="SUBMIT",
            command=self.submit,
            width=620, height=90,
            corner_radius=D.RADIUS,
            fg_color=D.G700,
            hover_color=D.G800,
            font=F(36, "bold"),
            text_color=D.T_WHITE
        ).pack()

        ctk.CTkLabel(
            inner,
            text="Your number is only used for system alerts.\nWe never share your information.",
            font=F(22), text_color=D.T_LIGHT, justify="center"
        ).pack(pady=(22, 0))

        # Attach in-app virtual keyboard to all entry fields in this window
        if _KB_AVAILABLE:
            self._kb = KeyboardManager(self)
            self._kb.bind_all(self)

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
def _send_login_sms(phone: str):
    try:
        from hardware.hardware_interface import get_hardware
        hw = get_hardware()
        if hw and hw.connected:
            from datetime import datetime as _dt
            timestamp = _dt.now().strftime("%b %d, %Y at %I:%M %p")
            hw.send_sms(phone,
                f"Smart Sprayer: Logged in successfully on {timestamp}. "
                "If this was not you, please check the system.")
            print(f"✓ Login SMS sent to {phone}")
    except Exception as e:
        print(f"⚠️ Login SMS error: {e}")


def _run_session():
    """Run login → optional phone setup → main UI.
    Returns 'logout' if the user logged out, None otherwise."""
    # Ensure account credentials are synced to Firebase RTDB before showing login
    try:
        from core.firebase_service import get_firebase_service
        from core.session import get_username, get_password
        fb = get_firebase_service()
        if fb.connected:
            fb.sync_account_to_rtdb(get_username(), get_password())
    except Exception as e:
        print(f"⚠️ RTDB account sync error: {e}")

    LoginScreen().mainloop()

    saved_phone = ""
    try:
        from core.session import get_phone
        saved_phone = get_phone() or ""
    except Exception as e:
        print(f"⚠️ Session read error: {e}")

    if saved_phone:
        _send_login_sms(saved_phone)
    else:
        MobileNumberScreen().mainloop()

    try:
        from ui.main_ui import main as ui_main
        return ui_main()   # returns 'logout' or None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    show_splash_screen()
    WelcomeScreen().mainloop()

    # Loop so that logging out always returns to the login screen
    while True:
        result = _run_session()
        if result != "logout":
            break


if __name__ == "__main__":
    main()
