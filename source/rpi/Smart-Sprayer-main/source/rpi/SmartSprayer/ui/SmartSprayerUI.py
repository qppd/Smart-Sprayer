import customtkinter as ctk
from PIL import Image
import os
import sys
import threading
import time
from datetime import datetime

# --- Mocking missing services for demonstration ---
# Replace these with your actual 'core' imports
class MockWeather:
    def get_current_weather(self):
        return {'temp': 28, 'humidity': 65, 'wind': 12}

class MockHardware:
    connected = True
    def get_both_tank_levels(self):
        return {"tank1": 75, "tank2": 40}

class MockScheduler:
    def get_next_schedule(self):
        return {'date': 'Oct 24', 'time': '08:00 AM', 'spray_type': 'Fertilizer', 'container': 'Tank 1'}
    def get_time_until_next_spray(self):
        return "02h 15m"

# --- UI CONSTANTS ---
BG_COLOR = "#D5E3D8"      # Light Sage Green
PRIMARY_TEXT = "#1B3022"  # Deep Forest Green
BTN_COLOR = "#558B2F"      # Grass Green
BTN_HOVER = "#467226"      # Darker Green

# =====================================================
# OVERLAYS (Login & Mobile)
# =====================================================

class LoginOverlay(ctk.CTkToplevel):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.VALID_USER = "automatedsprayer"
        self.VALID_PASS = "sprayer123"
        
        self.attributes("-fullscreen", True)
        self.configure(fg_color=BG_COLOR)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.container, text="Sign In", font=("Helvetica Bold", 42), text_color=PRIMARY_TEXT).pack(pady=10)
        
        self.user_entry = ctk.CTkEntry(self.container, placeholder_text="Username", width=420, height=55, corner_radius=25)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.container, placeholder_text="Password", show="*", width=420, height=55, corner_radius=25)
        self.pass_entry.pack(pady=10)

        self.error_label = ctk.CTkLabel(self.container, text="", text_color="#D32F2F")
        self.error_label.pack(pady=5)

        ctk.CTkButton(self.container, text="LOG IN", fg_color=BTN_COLOR, hover_color=BTN_HOVER, 
                      height=65, width=420, corner_radius=32, command=self.validate).pack(pady=10)

    def validate(self):
        if self.user_entry.get() == self.VALID_USER and self.pass_entry.get() == self.VALID_PASS:
            self.destroy()
            self.on_login_success()
        else:
            self.error_label.configure(text="Invalid credentials")

class MobileOverlay(ctk.CTkToplevel):
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.on_complete = on_complete
        self.attributes("-fullscreen", True)
        self.configure(fg_color=BG_COLOR)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.container, text="Mobile Registration", font=("Helvetica Bold", 32), text_color=PRIMARY_TEXT).pack(pady=10)
        
        self.mobile_entry = ctk.CTkEntry(self.container, placeholder_text="9XXXXXXXXX", width=340, height=55, corner_radius=25)
        self.mobile_entry.pack(pady=20)

        ctk.CTkButton(self.container, text="SUBMIT", fg_color=BTN_COLOR, height=65, width=420, corner_radius=32, 
                      command=lambda: [self.destroy(), self.on_complete()]).pack()

# =====================================================
# DASHBOARD PANEL (Integrated)
# =====================================================

class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent, hardware, scheduler):
        super().__init__(parent, fg_color="#F4F8F5")
        self.hardware = hardware
        self.scheduler = scheduler
        self.weather_service = MockWeather() # Replace with get_weather_service()

        self._build_ui()
        threading.Thread(target=self._update_loop, daemon=True).start()

    def card(self, parent):
        return ctk.CTkFrame(parent, fg_color="white", corner_radius=25)

    def big_value(self, parent, icon, text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=6)
        ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=40)).pack(side="left", padx=10)
        label = ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=28, weight="bold"), text_color="#1B5E20")
        label.pack(side="left")
        return label

    def tank_card(self, parent, title):
        card = self.card(parent)
        card.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18), text_color="#4CAF50").pack(anchor="w", padx=20, pady=(15, 5))
        bar = ctk.CTkProgressBar(card, height=28)
        bar.pack(fill="x", padx=20, pady=10)
        value = ctk.CTkLabel(card, text="0 %", font=ctk.CTkFont(size=30, weight="bold"), text_color="#1B5E20")
        value.pack(pady=(0, 15))
        return bar, value

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header, text="🌱 SMART SPRAYER", font=ctk.CTkFont(size=34, weight="bold"), text_color="#1B5E20").pack(side="left")
        self.time_label = ctk.CTkLabel(header, font=ctk.CTkFont(size=18), text_color="#4CAF50")
        self.time_label.pack(side="right")

        # Status & Weather Row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=30)
        
        status_card = self.card(top)
        status_card.pack(side="left", expand=True, fill="both", padx=10)
        self.status_icon = ctk.CTkLabel(status_card, text="🟢", font=ctk.CTkFont(size=80))
        self.status_icon.pack(pady=5)
        self.status_text = ctk.CTkLabel(status_card, text="IDLE", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1B5E20")
        self.status_text.pack()
        self.countdown = ctk.CTkLabel(status_card, text="Next: --", font=ctk.CTkFont(size=18), text_color="#558B2F")
        self.countdown.pack(pady=(0, 20))

        weather = self.card(top)
        weather.pack(side="left", expand=True, fill="both", padx=10)
        self.w_temp = self.big_value(weather, "🌡", "-- °C")
        self.w_hum = self.big_value(weather, "💧", "-- %")

        # Tanks Row
        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.pack(fill="x", padx=30, pady=20)
        self.tank1_bar, self.tank1_val = self.tank_card(mid, "🛢 TANK 1")
        self.tank2_bar, self.tank2_val = self.tank_card(mid, "🛢 TANK 2")

    def _update_loop(self):
        while True:
            self.after(0, self._update_ui_data)
            time.sleep(1)

    def _update_ui_data(self):
        self.time_label.configure(text=datetime.now().strftime("%b %d %Y  %I:%M:%S %p"))
        # Weather
        w = self.weather_service.get_current_weather()
        self.w_temp.configure(text=f"{w['temp']} °C")
        self.w_hum.configure(text=f"{w['humidity']} %")
        # Tanks
        levels = self.hardware.get_both_tank_levels()
        self._update_tank_bar(levels['tank1'], self.tank1_bar, self.tank1_val)
        self._update_tank_bar(levels['tank2'], self.tank2_bar, self.tank2_val)

    def _update_tank_bar(self, lvl, bar, label):
        bar.set(lvl/100)
        label.configure(text=f"{lvl}%")
        color = "#4CAF50" if lvl > 50 else "#FFC107" if lvl > 20 else "#F44336"
        bar.configure(progress_color=color)

# =====================================================
# MAIN APPLICATION
# =====================================================

class SmartSprayerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw() # Hide main window during login
        self.attributes("-fullscreen", True)
        
        # Initialize Logic
        self.hardware = MockHardware()
        self.scheduler = MockScheduler()

        # Build UI Container
        self.main_container = DashboardPanel(self, self.hardware, self.scheduler)
        self.main_container.pack(fill="both", expand=True)

        # Start Sequence
        self.launch_login_flow()

    def launch_login_flow(self):
        LoginOverlay(self, on_login_success=self.launch_mobile_flow)

    def launch_mobile_flow(self):
        MobileOverlay(self, on_complete=self.reveal_dashboard)

    def reveal_dashboard(self):
        self.deiconify()

if __name__ == "__main__":
    app = SmartSprayerUI()
    app.mainloop()