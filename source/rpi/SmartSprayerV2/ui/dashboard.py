# dashboard.py
# Dashboard with animated GIF weather icons – modernized design

import customtkinter as ctk
from datetime import datetime
import threading
import time
from PIL import Image
import os
from core.weather_service import get_weather_service

BG    = "#EAF4EF"
CARD  = "#F2F8F5"
GREEN = "#2E7D32"
BLUE  = "#1E88E5"

ACCENT_GREEN = "#81C784"
ACCENT_BLUE  = "#64B5F6"

PILL_GREEN_BG = "#E0F0E3"
PILL_BLUE_BG  = "#E3F2FD"

SCHEDULE_INNER = "#E9F5F0"

_UI_DIR    = os.path.dirname(os.path.abspath(__file__))
_ICONS_DIR = os.path.join(_UI_DIR, "assets", "icons")


def _icon(name):
    return os.path.join(_ICONS_DIR, name)


def _load_png(fname, size=(40, 40)):
    path = _icon(fname)
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"Could not load '{path}': {e}")
        return None


def _get_saved_location():
    """Read the saved barangay + municipality from data_store."""
    try:
        from core.data_store import get_location
        loc = get_location()
        if loc and loc.get("barangay") and loc.get("municipality"):
            return f"{loc['barangay']}, {loc['municipality']}"
    except Exception as e:
        print(f"Could not read location: {e}")
    return None


class AnimatedGIF:
    def __init__(self, label: ctk.CTkLabel, path: str, size=(100, 100)):
        self.label    = label
        self.size     = size
        self.frames   = []
        self.delays   = []
        self._job     = None
        self._idx     = 0
        self._running = False
        self._load(path)

    def _load(self, path: str):
        if not os.path.exists(path):
            return
        try:
            gif = Image.open(path)
            while True:
                frame = gif.copy().convert("RGBA").resize(self.size, Image.LANCZOS)
                self.frames.append(
                    ctk.CTkImage(light_image=frame, dark_image=frame, size=self.size)
                )
                delay = gif.info.get("duration", 100)
                self.delays.append(max(delay, 40))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"AnimatedGIF could not load '{path}': {e}")

    def start(self):
        if not self.frames:
            return
        self._running = True
        self._next_frame()

    def stop(self):
        self._running = False
        if self._job:
            try:
                self.label.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _next_frame(self):
        if not self._running or not self.frames:
            return
        self.label.configure(image=self.frames[self._idx], text="")
        delay = self.delays[self._idx]
        self._idx = (self._idx + 1) % len(self.frames)
        self._job = self.label.after(delay, self._next_frame)

    @property
    def loaded(self):
        return len(self.frames) > 0


class DashboardPanel(ctk.CTkFrame):

    def __init__(self, parent, hardware, scheduler):
        super().__init__(parent)

        self.hardware        = hardware
        self.scheduler       = scheduler
        self.weather_service = get_weather_service()

        self.last_tank1_level = 0.0
        self.last_tank2_level = 0.0
        self.update_counter   = 0

        self._raw_t1:       float | None = None
        self._raw_t2:       float | None = None
        self._raw_weather:  dict  | None = None
        self._raw_forecast: dict  | None = None

        self._tank1_low_alert_sent = False
        self._tank2_low_alert_sent = False
        self._TANK_LOW_THRESHOLD = 10.0

        self.configure(fg_color=BG)

        self._current_anim: AnimatedGIF | None = None

        self._load_static_icons()
        self._create_widgets()

        self.running = True
        threading.Thread(target=self._fetch_data_loop, daemon=True).start()
        self.after(1000, self._update_loop)

    def _load_static_icons(self):
        self.static_icons = {}
        for key, fname in [
            ("sunny",         "sunny.png"),
            ("cloudy",        "cloudy.png"),
            ("rainy",         "rainy.png"),
            ("partly_cloudy", "partly_cloudy.png"),
        ]:
            path = _icon(fname)
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    self.static_icons[key] = ctk.CTkImage(
                        light_image=img, dark_image=img, size=(100, 100)
                    )
                except Exception:
                    pass

    def _card(self, parent, accent_color=None):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        inner = ctk.CTkFrame(
            wrapper,
            fg_color=CARD,
            corner_radius=20,
            border_width=1,
            border_color="#D6EEE0",
        )
        inner.pack(fill="both", expand=True)
        wrapper._inner = inner
        return wrapper

    def _card_inner(self, card_wrapper):
        return card_wrapper._inner

    def _create_widgets(self):

        # ── TOP ROW ──────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)

        status_wrap = self._card(top, accent_color=ACCENT_GREEN)
        status_wrap.pack(side="left", expand=True, fill="both", padx=(0, 8))
        status_inner = self._card_inner(status_wrap)
        status_inner.configure(fg_color=CARD)

        pill = ctk.CTkFrame(status_inner, fg_color=PILL_GREEN_BG, corner_radius=99)
        pill.pack(anchor="w", padx=22, pady=(20, 0))

        pill_inner = ctk.CTkFrame(pill, fg_color="transparent")
        pill_inner.pack(padx=12, pady=6)

        self._status_dot = ctk.CTkLabel(
            pill_inner, text="●", font=("Arial", 18), text_color=GREEN, width=22,
        )
        self._status_dot.pack(side="left", padx=(0, 4))

        ctk.CTkLabel(
            pill_inner, text="SYSTEM",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=GREEN,
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_inner, text="IDLE",
            font=ctk.CTkFont(size=60, weight="bold"), text_color=GREEN, anchor="w",
        )
        self.status_label.pack(anchor="w", padx=22, pady=(8, 0))

        self.countdown_label = ctk.CTkLabel(
            status_inner, text="Time until spray: --",
            font=ctk.CTkFont(size=26), text_color=BLUE, anchor="w",
        )
        self.countdown_label.pack(anchor="w", padx=22, pady=(4, 0))

        self.debug_label = ctk.CTkLabel(
            status_inner, text="Updates: 0",
            font=ctk.CTkFont(size=15), text_color="#9DB8A8", anchor="w",
        )
        self.debug_label.pack(anchor="w", padx=22, pady=(6, 20))

        sched_wrap = self._card(top, accent_color=ACCENT_BLUE)
        sched_wrap.pack(side="left", expand=True, fill="both", padx=(8, 0))
        sched_inner = self._card_inner(sched_wrap)
        sched_inner.configure(fg_color=CARD)

        header = ctk.CTkFrame(sched_inner, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 0))

        ctk.CTkLabel(
            header, text="Next Schedule Spray",
            font=ctk.CTkFont(size=30, weight="bold"), text_color=GREEN,
        ).pack(side="left")

        bell_bg = ctk.CTkFrame(header, fg_color=PILL_BLUE_BG, corner_radius=12, width=48, height=48)
        bell_bg.pack(side="right")
        bell_bg.pack_propagate(False)

        bell_icon = _load_png("bell.png", size=(30, 30))
        ctk.CTkLabel(
            bell_bg, text="" if bell_icon else "🔔", image=bell_icon, font=("Arial", 24),
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(sched_inner, height=1, fg_color="#D6EEE0", corner_radius=0).pack(
            fill="x", padx=0, pady=(14, 0)
        )

        self.schedule_item = ctk.CTkFrame(
            sched_inner, fg_color=SCHEDULE_INNER, corner_radius=14,
            border_width=1, border_color="#C8E6C9",
        )
        self.schedule_item.pack(fill="both", expand=True, padx=16, pady=14)

        date_row = ctk.CTkFrame(self.schedule_item, fg_color="transparent")
        date_row.pack(fill="x", padx=14, pady=(12, 0))

        self.schedule_datetime = ctk.CTkLabel(
            date_row, text="No upcoming schedules",
            font=ctk.CTkFont(size=26, weight="bold"), text_color="#2E7D32", anchor="w",
        )
        self.schedule_datetime.pack(side="left")

        self.schedule_type = ctk.CTkLabel(
            date_row, text="", fg_color="#22C55E", text_color="white",
            corner_radius=8, font=ctk.CTkFont(size=18, weight="bold"), padx=14, pady=8,
        )
        self.schedule_type.pack(side="right")

        info_row = ctk.CTkFrame(self.schedule_item, fg_color="transparent")
        info_row.pack(fill="x", padx=14, pady=(10, 14))

        def _meta_chip(parent, emoji, var_attr, default_text):
            chip = ctk.CTkFrame(parent, fg_color="#E0F0E3", corner_radius=8)
            chip.pack(side="left", padx=(0, 10))
            chip_inner = ctk.CTkFrame(chip, fg_color="transparent")
            chip_inner.pack(padx=10, pady=7)
            ctk.CTkLabel(chip_inner, text=emoji, font=("Arial", 18)).pack(side="left", padx=(0, 6))
            lbl = ctk.CTkLabel(
                chip_inner, text=default_text,
                font=ctk.CTkFont(size=20), text_color="#555",
            )
            lbl.pack(side="left")
            return lbl

        self.schedule_container = _meta_chip(info_row, "📦", None, "Container: --")
        self.schedule_volume    = _meta_chip(info_row, "💧", None, "Volume: -- ml")
        self.schedule_duration  = _meta_chip(info_row, "⏱",  None, "Duration: -- s")

        # ── BOTTOM ROW ────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=20, pady=10)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_columnconfigure(2, weight=2)
        bottom.grid_rowconfigure(0, weight=1)

        self._build_container(bottom, "Container 1", 1)
        self._build_container(bottom, "Container 2", 2)
        self._build_weather(bottom)

    def _build_container(self, parent, title, num):

        wrap = self._card(parent, accent_color=ACCENT_GREEN)
        wrap.grid(row=0, column=num - 1, sticky="nsew", padx=(0, 8))
        card = self._card_inner(wrap)

        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.pack(fill="x", padx=20, pady=(22, 0))

        ctk.CTkLabel(
            title_row, text=title,
            font=ctk.CTkFont(size=30, weight="bold"), text_color=GREEN,
        ).pack(side="left")

        status_badge = ctk.CTkLabel(
            title_row, text="CRITICAL",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFEBEE", text_color="#E53935",
            corner_radius=8, padx=14, pady=8,
        )
        status_badge.pack(side="right")

        import tkinter as tk

        tank_frame = ctk.CTkFrame(card, fg_color="transparent")
        tank_frame.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        canvas = tk.Canvas(tank_frame, bg="#E8F5EC", highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        canvas._level = 0.0
        canvas._num   = num

        def _draw_tank(event=None):
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 2 or h < 2:
                return
            canvas.delete("all")
            level  = canvas._level
            r      = 16
            _rounded_rect(canvas, 0, 0, w, h, r, fill="#E8F5EC", outline="")
            fill_h = h * level
            if fill_h > 1:
                fill_color = (
                    "#E53935" if level < 0.20 else
                    "#FB8C00" if level < 0.50 else
                    "#2E7D32"
                )
                _rounded_rect(canvas, 0, h - fill_h, w, h, r, fill=fill_color, outline="")
            pct_color = "white" if fill_h > h * 0.55 else (
                "#E53935" if level < 0.20 else
                "#FB8C00" if level < 0.50 else
                "#2E7D32"
            )
            canvas.create_text(
                w / 2, h / 2 - 18,
                text=f"{level*100:.0f}%",
                font=("Arial", 64, "bold"),
                fill=pct_color,
            )
            canvas.create_text(
                w / 2, h / 2 + 46,
                text="Tank Level",
                font=("Arial", 20),
                fill=pct_color if fill_h > h * 0.55 else "#6A8A7A",
            )

        def _rounded_rect(cv, x1, y1, x2, y2, r, **kw):
            pts = [
                x1+r, y1,  x2-r, y1,
                x2,   y1,  x2,   y1+r,
                x2,   y2-r,x2,   y2,
                x2-r, y2,  x1+r, y2,
                x1,   y2,  x1,   y2-r,
                x1,   y1+r,x1,   y1,
            ]
            cv.create_polygon(pts, smooth=True, **kw)

        canvas.bind("<Configure>", lambda e: _draw_tank())
        canvas._draw = _draw_tank

        bar = ctk.CTkProgressBar(card, height=0, progress_color="#E53935", fg_color="#D6EEE0")
        bar.pack(fill="x", padx=20, pady=0)
        bar.set(0)
        bar._canvas = canvas

        _orig_set = bar.set
        def _patched_set(value, **kw):
            _orig_set(value, **kw)
            canvas._level = value
            canvas._draw()
        bar.set = _patched_set

        percent = ctk.CTkLabel(card, text="", width=0, height=0, fg_color="transparent")
        percent._canvas = canvas
        def _patched_conf(**kw):
            pass
        percent.configure = _patched_conf

        liters = ctk.CTkLabel(
            card, text="0.0 L / 16.0 L",
            font=ctk.CTkFont(size=26, weight="bold"), text_color="#2E7D32",
        )
        liters.pack(anchor="center", pady=(8, 22))

        if num == 1:
            self.tank1_progress = bar
            self.tank1_label    = percent
            self.tank1_liters   = liters
            self.tank1_status   = status_badge
        else:
            self.tank2_progress = bar
            self.tank2_label    = percent
            self.tank2_liters   = liters
            self.tank2_status   = status_badge

    def _build_weather(self, parent):

        wrap = self._card(parent, accent_color="#64B5F6")
        wrap.grid(row=0, column=2, sticky="nsew", padx=(0, 0))
        self.weather_card = self._card_inner(wrap)

        top_section = ctk.CTkFrame(self.weather_card, fg_color="transparent")
        top_section.pack(fill="x", padx=20, pady=(18, 0))

        # ── HEADER ROW: title left, location badge right ──────────────────────
        header_row = ctk.CTkFrame(top_section, fg_color="transparent")
        header_row.pack(fill="x")

        ctk.CTkLabel(
            header_row, text="Current Weather",
            font=ctk.CTkFont(size=22), text_color=GREEN,
        ).pack(side="left", anchor="w")

        # Location badge
        saved_loc = _get_saved_location()
        loc_text  = saved_loc if saved_loc else "Location not set"

        self.weather_location_badge = ctk.CTkFrame(
            header_row, fg_color=PILL_GREEN_BG, corner_radius=10
        )
        self.weather_location_badge.pack(side="right")

        self.weather_location_label = ctk.CTkLabel(
            self.weather_location_badge,
            text=f"  {loc_text}  ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=GREEN,
            padx=6, pady=4
        )
        self.weather_location_label.pack()

        self.weather_condition = ctk.CTkLabel(
            top_section, text="Loading...",
            font=ctk.CTkFont(size=32, weight="bold"), text_color=GREEN,
        )
        self.weather_condition.pack(anchor="w", pady=(4, 0))

        mid = ctk.CTkFrame(self.weather_card, fg_color="transparent")
        mid.pack(fill="x", padx=20, pady=(10, 0))

        self.weather_icon = ctk.CTkLabel(mid, text="", width=90, height=90)
        self.weather_icon.pack(side="left", padx=(0, 14))

        temp_block = ctk.CTkFrame(mid, fg_color="transparent")
        temp_block.pack(side="left")

        self.weather_temp = ctk.CTkLabel(
            temp_block, text="--°",
            font=ctk.CTkFont(size=86, weight="bold"), text_color="#1A1A2E",
        )
        self.weather_temp.pack(anchor="w")

        self.weather_feels_like = ctk.CTkLabel(
            temp_block, text="Feels like --°C",
            font=ctk.CTkFont(size=22), text_color="#5A7A6A",
        )
        self.weather_feels_like.pack(anchor="w")

        ctk.CTkFrame(self.weather_card, height=2, fg_color="#D6EEE0", corner_radius=0).pack(
            fill="x", padx=20, pady=(16, 12)
        )

        pills = ctk.CTkFrame(self.weather_card, fg_color="transparent")
        pills.pack(fill="both", expand=True, padx=16, pady=(0, 18))
        pills.grid_columnconfigure((0, 1, 2), weight=1)
        pills.grid_rowconfigure(0, weight=1)

        wind_img     = _load_png("wind.png",        size=(48, 48))
        humidity_img = _load_png("humidity.png",    size=(48, 48))
        temp_img     = _load_png("temperature.png", size=(48, 48))

        def _pill(parent, col, img, fallback_emoji, label):
            box = ctk.CTkFrame(
                parent, fg_color="#E8F5EC", corner_radius=14,
                border_width=1, border_color="#C8E6C9",
            )
            box.grid(row=0, column=col, sticky="nsew", padx=5)
            inner = ctk.CTkFrame(box, fg_color="transparent")
            inner.place(relx=0.5, rely=0.5, anchor="center")
            if img:
                ctk.CTkLabel(inner, text="", image=img).pack(pady=(0, 6))
            else:
                ctk.CTkLabel(inner, text=fallback_emoji, font=("Arial", 34)).pack(pady=(0, 6))
            val = ctk.CTkLabel(
                inner, text="--",
                font=ctk.CTkFont(size=28, weight="bold"), text_color="#1A1A2E",
            )
            val.pack()
            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(size=17), text_color="#6A8A7A",
            ).pack(pady=(6, 0))
            return val

        self.weather_wind     = _pill(pills, 0, wind_img,     "💨", "Wind")
        self.weather_humidity = _pill(pills, 1, humidity_img, "💧", "Humidity")
        self.weather_uv       = _pill(pills, 2, temp_img,     "🌡", "Min / Max \nTemperature")

        # ── RAIN FORECAST SECTION ──────────────────────────────────────────────
        ctk.CTkFrame(self.weather_card, height=1, fg_color="#D6EEE0", corner_radius=0).pack(
            fill="x", padx=0, pady=(12, 0)
        )

        forecast_section = ctk.CTkFrame(
            self.weather_card,
            fg_color="#E9F5F0",
            corner_radius=10,
            border_width=1,
            border_color="#C8E6C9",
        )
        forecast_section.pack(fill="x", padx=12, pady=(6, 10))

        forecast_header = ctk.CTkFrame(forecast_section, fg_color="transparent")
        forecast_header.pack(fill="x", padx=8, pady=(6, 2))

        self.forecast_icon_label = ctk.CTkLabel(forecast_header, text="", width=40, height=40)
        self.forecast_icon_label.pack(side="left", padx=(2, 6))
        self._forecast_anim = AnimatedGIF(self.forecast_icon_label, _icon("rainy.gif"), size=(40, 40))
        if self._forecast_anim.loaded:
            self._forecast_anim.start()

        ctk.CTkLabel(
            forecast_header, text="RAIN FORECAST",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=GREEN,
        ).pack(side="left")

        forecast_row = ctk.CTkFrame(forecast_section, fg_color="transparent")
        forecast_row.pack(fill="x", padx=8, pady=(0, 4))

        today_box = ctk.CTkFrame(
            forecast_row, fg_color="#E0F0E3",
            corner_radius=8, border_width=1, border_color="#C8E6C9",
        )
        today_box.pack(side="left", expand=True, fill="both", padx=(0, 4), pady=2)

        ctk.CTkLabel(
            today_box, text="TODAY",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2E7D32",
        ).pack(pady=(5, 1))

        self.forecast_today_chance = ctk.CTkLabel(
            today_box, text="--%",
            font=ctk.CTkFont(size=32, weight="bold"), text_color="#4CAF50",
        )
        self.forecast_today_chance.pack()

        self.forecast_today_precip = ctk.CTkLabel(
            today_box, text="-- mm",
            font=ctk.CTkFont(size=18), text_color="#5A7A6A",
        )
        self.forecast_today_precip.pack(pady=(0, 5))

        tomorrow_box = ctk.CTkFrame(
            forecast_row, fg_color="#E0F0E3",
            corner_radius=8, border_width=1, border_color="#C8E6C9",
        )
        tomorrow_box.pack(side="left", expand=True, fill="both", padx=(4, 0), pady=2)

        ctk.CTkLabel(
            tomorrow_box, text="TOMORROW",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2E7D32",
        ).pack(pady=(5, 1))

        self.forecast_tomorrow_chance = ctk.CTkLabel(
            tomorrow_box, text="--%",
            font=ctk.CTkFont(size=32, weight="bold"), text_color="#4CAF50",
        )
        self.forecast_tomorrow_chance.pack()

        self.forecast_tomorrow_precip = ctk.CTkLabel(
            tomorrow_box, text="-- mm",
            font=ctk.CTkFont(size=18), text_color="#5A7A6A",
        )
        self.forecast_tomorrow_precip.pack(pady=(0, 5))

        self.forecast_alert = ctk.CTkLabel(
            forecast_section, text="",
            font=ctk.CTkFont(size=17, weight="bold"), text_color="#E65100",
        )
        self.forecast_alert.pack(pady=(0, 6))

        self._play_weather_gif("cloudy")

    # ── GIF ANIMATION ─────────────────────────────────────────────────────────

    def _play_weather_gif(self, condition_key: str):
        if self._current_anim:
            self._current_anim.stop()
            self._current_anim = None
        gif_path = _icon(f"{condition_key}.gif")
        anim = AnimatedGIF(self.weather_icon, gif_path, size=(100, 100))
        if anim.loaded:
            self._current_anim = anim
            anim.start()
        else:
            static = self.static_icons.get(condition_key)
            if static:
                self.weather_icon.configure(image=static, text="")
            else:
                fallback = {
                    "sunny": "☀️", "cloudy": "☁️",
                    "rainy": "🌧️", "partly_cloudy": "⛅",
                }
                self.weather_icon.configure(
                    image=None,
                    text=fallback.get(condition_key, "🌤️"),
                    font=("Arial", 64),
                )

    def _condition_key(self, condition: str) -> str:
        c = condition.lower()
        if "rain" in c or "drizzle" in c or "shower" in c:
            return "rainy"
        if "cloud" in c or "overcast" in c:
            return "cloudy"
        if "sun" in c or "clear" in c:
            return "sunny"
        return "partly_cloudy"

    # ── DATA FETCH LOOP (background thread) ───────────────────────────────────

    def _fetch_data_loop(self):
        while self.running:
            if self.hardware:
                try:
                    levels = self.hardware.get_both_tank_levels()
                    t1 = levels.get('tank1')
                    t2 = levels.get('tank2')
                    if t1 is not None:
                        self._raw_t1 = t1
                    if t2 is not None:
                        self._raw_t2 = t2
                except Exception:
                    pass

            if self.weather_service and self.weather_service.available:
                try:
                    w = self.weather_service.get_current_weather_cached()
                    if w:
                        self._raw_weather = w
                    f = self.weather_service.get_forecast_data_cached()
                    if f:
                        self._raw_forecast = f
                except Exception:
                    pass

            time.sleep(2)

    # ── UPDATE LOOP (main thread) ──────────────────────────────────────────────

    def _update_loop(self):
        if not self.running:
            return
        try:
            self.update_counter += 1
            self._update_tank_levels()
            self._update_next_schedule()
            self._update_weather()
            self._update_debug_counter()
            self._refresh_location_badge()
        except Exception as e:
            print(f"Dashboard UI update error: {e}")
        try:
            self.after(1000, self._update_loop)
        except Exception:
            pass

    def _refresh_location_badge(self):
        """Periodically re-read the saved location so badge updates if user changes it in Settings."""
        if self.update_counter % 10 != 0:
            return
        saved_loc = _get_saved_location()
        loc_text  = f"  {saved_loc}  " if saved_loc else "  Location not set  "
        try:
            self.weather_location_label.configure(text=loc_text)
        except Exception:
            pass

    def _update_debug_counter(self):
        self.debug_label.configure(text=f"Updates: {self.update_counter}")

    def _update_next_schedule(self):
        try:
            next_schedule = self.scheduler.get_next_schedule()
        except Exception:
            next_schedule = None

        if not isinstance(next_schedule, dict) or not next_schedule:
            self.schedule_datetime.configure(text="No upcoming schedules")
            self.schedule_container.configure(text="Container: --")
            self.schedule_volume.configure(text="Volume: -- ml")
            self.schedule_duration.configure(text="Duration: -- s")
            self.schedule_type.configure(text="")
            self.status_label.configure(text="IDLE", text_color=GREEN)
            self.countdown_label.configure(text="Time until spray: --")
            return

        date       = next_schedule.get("date", "--")
        time_      = next_schedule.get("time", "--")
        container  = next_schedule.get("container", "--")
        spray_type = next_schedule.get("spray_type", "Spray")
        volume     = float(next_schedule.get("volume_ml", 0))

        try:
            target         = datetime.strptime(f"{date} {time_}", "%Y-%m-%d %H:%M")
            now            = datetime.now()
            remaining      = (target - now).total_seconds()
            formatted_date = target.strftime("%b %d, %Y at %I:%M %p")
        except Exception:
            formatted_date = f"{date} at {time_}"
            remaining      = None

        try:
            duration = self.scheduler.calculate_spray_duration(volume)
        except Exception:
            duration = 0

        self.schedule_datetime.configure(text=formatted_date)
        self.schedule_container.configure(text=f"Container: {container}")
        self.schedule_volume.configure(text=f"Volume: {volume:.0f} ml")
        self.schedule_duration.configure(text=f"Duration: {duration:.1f} s")

        color_map = {"fertilizer": "#22C55E", "pesticide": "#EF4444"}
        self.schedule_type.configure(
            text=spray_type.upper(),
            fg_color=color_map.get(spray_type.lower(), "#3B82F6"),
        )

        if remaining is not None:
            if remaining <= 0:
                self.status_label.configure(text="SPRAYING", text_color="#E74C3C")
                self.countdown_label.configure(text="Spraying now...")
            else:
                self.status_label.configure(text="SCHEDULED", text_color=BLUE)
                h = int(remaining // 3600)
                m = int((remaining % 3600) // 60)
                s = int(remaining % 60)
                self.countdown_label.configure(
                    text=f"Time until spray: {h:02d}:{m:02d}:{s:02d}"
                )
        else:
            self.status_label.configure(text="SCHEDULED", text_color=BLUE)
            self.countdown_label.configure(text="Time until spray: --")

    def _update_tank_levels(self):
        t1 = self._raw_t1
        t2 = self._raw_t2

        self._check_tank_low_level_sms(1, t1)
        self._check_tank_low_level_sms(2, t2)

        try:
            for level, prog, lbl, lit, badge in [
                (t1, self.tank1_progress, self.tank1_label, self.tank1_liters, self.tank1_status),
                (t2, self.tank2_progress, self.tank2_label, self.tank2_liters, self.tank2_status),
            ]:
                if level is None:
                    continue

                prog.set(level / 100.0)
                liters_val = (level / 100.0) * 16.0

                if level < 20:
                    badge_text, badge_fg, badge_tc = "CRITICAL", "#FFEBEE", "#E53935"
                elif level < 50:
                    badge_text, badge_fg, badge_tc = "LOW", "#FFF3E0", "#FB8C00"
                else:
                    badge_text, badge_fg, badge_tc = "OK", "#E8F5EC", GREEN

                lit.configure(text=f"{liters_val:.1f} L / 16.0 L")
                badge.configure(text=badge_text, fg_color=badge_fg, text_color=badge_tc)

        except Exception as e:
            if self.update_counter % 30 == 0:
                print(f"Tank update error: {e}")

    def _update_weather(self):
        weather = self._raw_weather

        if not weather:
            self.weather_condition.configure(text="Weather unavailable", text_color=GREEN)
            self.weather_temp.configure(text="--°")
            self.weather_wind.configure(text="--")
            self.weather_humidity.configure(text="--")
            self.weather_feels_like.configure(text="Feels like --°C")
            self.weather_uv.configure(text="--")
            if self._current_anim is None or not self._current_anim.loaded:
                self._play_weather_gif("cloudy")
            return

        condition  = weather.get("condition", "")
        temp       = weather.get("temperature_c", 0)
        wind_ms    = weather.get("wind_kph", 0) / 3.6
        humidity   = weather.get("humidity", 0)
        feels_like = weather.get("feels_like_c", temp)
        temp_min   = weather.get("mintemp_c", temp - 2)
        temp_max   = weather.get("maxtemp_c", temp + 2)

        key = self._condition_key(condition)
        if not hasattr(self, "_last_condition_key") or self._last_condition_key != key:
            self._last_condition_key = key
            self._play_weather_gif(key)

        self.weather_condition.configure(text=f"{condition}", text_color=GREEN)
        self.weather_temp.configure(text=f"{temp:.0f}°")
        self.weather_wind.configure(text=f"{wind_ms:.1f} m/s")
        self.weather_humidity.configure(text=f"{humidity}%")
        self.weather_feels_like.configure(text=f"Feels like {feels_like:.0f}°C")
        self.weather_uv.configure(text=f"{temp_min:.0f}° / {temp_max:.0f}°")

        if self._raw_forecast:
            self._update_forecast_display(self._raw_forecast)

    def _update_forecast_display(self, forecast: dict):
        def chance_color(chance: int) -> str:
            if chance >= 70:   return "#F44336"
            elif chance >= 40: return "#FF9800"
            elif chance >= 20: return "#FBC02D"
            else:              return "#4CAF50"

        today    = forecast.get("today",    {})
        tomorrow = forecast.get("tomorrow", {})

        today_chance    = today.get("chance",    0)
        today_precip    = today.get("precip_mm", 0.0)
        tomorrow_chance = tomorrow.get("chance",    0)
        tomorrow_precip = tomorrow.get("precip_mm", 0.0)

        self.forecast_today_chance.configure(
            text=f"{today_chance}%", text_color=chance_color(today_chance))
        self.forecast_today_precip.configure(text=f"{today_precip:.1f} mm")

        self.forecast_tomorrow_chance.configure(
            text=f"{tomorrow_chance}%", text_color=chance_color(tomorrow_chance))
        self.forecast_tomorrow_precip.configure(text=f"{tomorrow_precip:.1f} mm")

        max_chance = max(today_chance, tomorrow_chance)
        if max_chance >= 70:
            self.forecast_alert.configure(
                text="High rain risk! Spraying may be auto-rescheduled.", text_color="#F44336")
        elif max_chance >= 40:
            self.forecast_alert.configure(
                text="Moderate rain chance. Monitor forecast.", text_color="#FF9800")
        else:
            self.forecast_alert.configure(
                text="Low rain risk. Safe to spray.", text_color="#4CAF50")

    def _get_spray_type_for_tank(self, tank_num):
        """Look up the spray type assigned to a container from active schedules."""
        try:
            container_name = f"Container {tank_num}"
            schedules = self.scheduler.data_store.get_active_schedules()
            for s in schedules:
                if s.get('container') == container_name:
                    return s.get('spray_type', 'Unknown')
        except Exception:
            pass
        return 'Unknown'

    def _check_tank_low_level_sms(self, tank_num, level):
        if level is None:
            return
        alert_sent = self._tank1_low_alert_sent if tank_num == 1 else self._tank2_low_alert_sent

        if level <= self._TANK_LOW_THRESHOLD and not alert_sent:
            self._send_tank_low_sms(tank_num, level)
            if tank_num == 1: self._tank1_low_alert_sent = True
            else:             self._tank2_low_alert_sent = True
        elif level > self._TANK_LOW_THRESHOLD and alert_sent:
            if tank_num == 1: self._tank1_low_alert_sent = False
            else:             self._tank2_low_alert_sent = False

    def _send_tank_low_sms(self, tank_num, level):
        def _do_send():
            try:
                from core.data_store import get_recipients
                recipients = get_recipients()
                if not recipients:
                    print(f"[SMS] No recipients configured — skipping tank {tank_num} low alert")
                    return
                spray_type = self._get_spray_type_for_tank(tank_num)
                if level == 0.0:
                    message = (
                        f"Alert: Empty {spray_type} container detected. "
                        f"Refill required before continuing spraying."
                    )
                else:
                    message = (
                        f"Alert: Critical {spray_type} level detected. "
                        f"Refill required before continuing spraying."
                    )
                if self.hardware and self.hardware.connected:
                    for r in recipients:
                        phone = r.get('phone', '')
                        if phone:
                            self.hardware.send_sms(phone, message)
                            print(f"[SMS] Tank {tank_num} {spray_type} alert sent to {phone}")
                else:
                    print(f"[SMS] Hardware not connected — could not send tank {tank_num} low alert")
            except Exception as e:
                print(f"[SMS] Error sending tank low alert: {e}")
        threading.Thread(target=_do_send, daemon=True).start()

    def cleanup(self):
        self.running = False
        if self._current_anim:
            self._current_anim.stop()
        if hasattr(self, "_forecast_anim") and self._forecast_anim:
            self._forecast_anim.stop()
