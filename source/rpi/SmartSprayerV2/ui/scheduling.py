# scheduling.py
# Scheduling UI — Modern Design Refresh (same green palette)

import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import uuid
import calendar


# ─────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────
class DS:
    # Greens
    G900 = "#1B5E20"
    G800 = "#2E7D32"
    G600 = "#388E3C"
    G500 = "#4CAF50"
    G400 = "#66BB6A"
    G200 = "#C8E6C9"
    G100 = "#E8F5E9"
    G50  = "#F1F8F2"

    # Neutrals
    WHITE   = "#FFFFFF"
    N50     = "#F7F8F7"
    N100    = "#EEF0EE"
    N200    = "#D8DDD8"
    N400    = "#9AA89A"
    N600    = "#555F55"
    N800    = "#2A2F2A"

    # Accents
    AMBER   = "#F59E0B"
    AMBER_D = "#D97706"
    RED     = "#EF4444"
    RED_D   = "#DC2626"
    BLUE    = "#0EA5E9"
    BLUE_D  = "#0284C7"

    # Fonts
    FONT_DISPLAY = ("Segoe UI", 26, "bold")
    FONT_HEADING = ("Segoe UI", 17, "bold")
    FONT_SUBHEAD = ("Segoe UI", 14, "bold")
    FONT_BODY    = ("Segoe UI", 13)
    FONT_SMALL   = ("Segoe UI", 11)
    FONT_MONO    = ("Consolas", 13)


def _font(size, weight="normal", family="Segoe UI"):
    return ctk.CTkFont(family=family, size=size, weight=weight if weight != "normal" else "normal")


class SchedulingPanel(ctk.CTkFrame):
    """Modern Scheduling Panel — green palette, elevated aesthetics."""

    def __init__(self, parent, scheduler, reschedule_mgr, logger, dashboard_callback=None):
        super().__init__(parent)
        self.scheduler       = scheduler
        self.reschedule_mgr  = reschedule_mgr
        self.logger          = logger
        self.dashboard_callback = dashboard_callback

        self.view_date     = datetime.now()
        self.selected_date = datetime.now()
        self.day_buttons   = {}

        self.configure(fg_color=DS.G50)
        self._create_widgets()
        self.refresh_schedule_list()

    # ══════════════════════════════════════════════════════
    #  MAIN LAYOUT
    # ══════════════════════════════════════════════════════
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_column()
        self._build_right_column()

    # ── LEFT COLUMN ───────────────────────────────────────
    def _build_left_column(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=24)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Section header
        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(
            hdr, text="Create Schedule",
            font=_font(24, "bold"), text_color=DS.G800
        ).pack(side="left")

        # Card
        card = ctk.CTkFrame(left, fg_color=DS.WHITE, corner_radius=16,
                             border_width=1, border_color=DS.N200)
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=DS.G200,
            scrollbar_button_hover_color=DS.G400,
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self._build_form(scroll)

    def _build_form(self, parent):
        pad = {"padx": 24}

        # ── DATE ──────────────────────────────
        self._section_label(parent, "Select Date").pack(anchor="w", pady=(20, 8), **pad)

        cal_card = ctk.CTkFrame(parent, fg_color=DS.G100, corner_radius=12,
                                 border_width=1, border_color=DS.G200)
        cal_card.pack(fill="x", **pad)

        # Month nav
        nav = ctk.CTkFrame(cal_card, fg_color="transparent")
        nav.pack(fill="x", padx=12, pady=(12, 4))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            nav, text="‹", width=34, height=34, corner_radius=17,
            fg_color=DS.G500, hover_color=DS.G600,
            font=_font(16, "bold"), command=self._prev_month
        ).grid(row=0, column=0, padx=(0, 6))

        self.cal_month_label = ctk.CTkLabel(
            nav, text="", font=_font(15, "bold"), text_color=DS.G800
        )
        self.cal_month_label.grid(row=0, column=1)

        ctk.CTkButton(
            nav, text="›", width=34, height=34, corner_radius=17,
            fg_color=DS.G500, hover_color=DS.G600,
            font=_font(16, "bold"), command=self._next_month
        ).grid(row=0, column=2, padx=(6, 0))

        # Days
        self.days_grid_frame = ctk.CTkFrame(cal_card, fg_color="transparent")
        self.days_grid_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._build_calendar_grid()

        # ── TIME ──────────────────────────────
        self._section_label(parent, "Select Time").pack(anchor="w", pady=(20, 8), **pad)

        time_row = ctk.CTkFrame(parent, fg_color="transparent")
        time_row.pack(anchor="w", **pad)

        self.hour_cb = self._dropdown(time_row, [f"{i:02d}" for i in range(1, 13)], "08", 80)
        self.hour_cb.pack(side="left")

        ctk.CTkLabel(time_row, text=":", font=_font(20, "bold"),
                     text_color=DS.N800).pack(side="left", padx=4)

        self.min_cb = self._dropdown(time_row, [f"{i:02d}" for i in range(0, 60, 5)], "00", 80)
        self.min_cb.pack(side="left")

        self.ampm_cb = self._dropdown(time_row, ["AM", "PM"], "AM", 76)
        self.ampm_cb.pack(side="left", padx=(10, 0))

        # ── SPRAY TYPE ────────────────────────
        self._section_label(parent, "Spray Type").pack(anchor="w", pady=(20, 8), **pad)

        self.spray_var = ctk.StringVar(value="Fertilizer")
        spray_row = ctk.CTkFrame(parent, fg_color="transparent")
        spray_row.pack(anchor="w", **pad)

        for val in ["Fertilizer", "Pesticide"]:
            self._radio_pill(spray_row, val, self.spray_var, val,
                             cmd=self._on_spray_type_change).pack(side="left", padx=(0, 10))

        # ── CONTAINER ─────────────────────────
        self._section_label(parent, "Container").pack(anchor="w", pady=(20, 8), **pad)

        self.cont_var = ctk.StringVar(value="Container 1")
        cont_row = ctk.CTkFrame(parent, fg_color="transparent")
        cont_row.pack(anchor="w", **pad)

        for val in ["Container 1", "Container 2"]:
            self._radio_pill(cont_row, val, self.cont_var, val).pack(side="left", padx=(0, 10))

        # ── VOLUME ────────────────────────────
        self._section_label(parent, "Spray Volume (mL)").pack(anchor="w", pady=(20, 8), **pad)

        vol_row = ctk.CTkFrame(parent, fg_color="transparent")
        vol_row.pack(anchor="w", **pad)

        self.vol_entry = ctk.CTkEntry(
            vol_row, width=110, height=38,
            fg_color=DS.WHITE, border_color=DS.G400, border_width=2,
            font=_font(14), text_color=DS.N800,
            placeholder_text="1000"
        )
        self.vol_entry.insert(0, "1000")
        self.vol_entry.pack(side="left")

        ctk.CTkLabel(vol_row, text="mL", font=_font(13, "bold"),
                     text_color=DS.N600).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            parent, text="Pump rate: 5 L/min  ·  Duration auto-calculated",
            font=_font(11), text_color=DS.N400
        ).pack(anchor="w", padx=24, pady=(3, 0))

        # ── RECURRING ────────────────────────
        self._section_label(parent, "Recurring (Optional)").pack(anchor="w", pady=(20, 8), **pad)

        self.recurring_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            parent, text="Enable recurring schedule",
            variable=self.recurring_var, command=self._toggle_recurring,
            font=_font(13), text_color=DS.N800,
            checkbox_width=22, checkbox_height=22,
            fg_color=DS.G500, hover_color=DS.G400,
            checkmark_color=DS.WHITE
        ).pack(anchor="w", **pad)

        self.recurring_frame = ctk.CTkFrame(
            parent, fg_color=DS.G100, corner_radius=10,
            border_width=1, border_color=DS.G200
        )

        ctk.CTkLabel(self.recurring_frame, text="Interval (days):",
                     font=_font(13), text_color=DS.N600
                     ).pack(anchor="w", padx=16, pady=(12, 2))
        self.interval_entry = ctk.CTkEntry(
            self.recurring_frame, height=38, fg_color=DS.WHITE,
            border_color=DS.G400, border_width=2, font=_font(13),
            placeholder_text="e.g., 7"
        )
        self.interval_entry.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(self.recurring_frame, text="Number of occurrences:",
                     font=_font(13), text_color=DS.N600
                     ).pack(anchor="w", padx=16, pady=(4, 2))
        self.count_entry = ctk.CTkEntry(
            self.recurring_frame, height=38, fg_color=DS.WHITE,
            border_color=DS.G400, border_width=2, font=_font(13),
            placeholder_text="e.g., 4"
        )
        self.count_entry.pack(fill="x", padx=16, pady=(0, 14))

        # ── CREATE BUTTON ─────────────────────
        ctk.CTkButton(
            parent,
            text="✦  Create Schedule",
            command=self._handle_create,
            fg_color=DS.G500, hover_color=DS.G600,
            height=52, corner_radius=12,
            font=_font(16, "bold"), text_color=DS.WHITE
        ).pack(fill="x", padx=24, pady=(22, 18))

    # ── RIGHT COLUMN ──────────────────────────────────────
    def _build_right_column(self):
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=24)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Header row
        hdr = ctk.CTkFrame(right, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="Active Schedules",
            font=_font(24, "bold"), text_color=DS.G800
        ).grid(row=0, column=0, sticky="w")

        btn_row = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_row.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_row, text="↻  Refresh",
            command=self.refresh_schedule_list,
            fg_color=DS.BLUE, hover_color=DS.BLUE_D,
            height=34, corner_radius=8,
            font=_font(13, "bold"), width=110
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="✕  Cancel All",
            command=self._cancel_all,
            fg_color=DS.RED, hover_color=DS.RED_D,
            height=34, corner_radius=8,
            font=_font(13, "bold"), width=120
        ).pack(side="left")

        # List card
        card = ctk.CTkFrame(right, fg_color=DS.WHITE, corner_radius=16,
                             border_width=1, border_color=DS.N200)
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        self.schedule_list = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=DS.G200,
            scrollbar_button_hover_color=DS.G400,
        )
        self.schedule_list.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # ══════════════════════════════════════════════════════
    #  HELPER WIDGETS
    # ══════════════════════════════════════════════════════
    def _section_label(self, parent, text):
        return ctk.CTkLabel(parent, text=text, font=_font(17, "bold"), text_color=DS.G800)

    def _dropdown(self, parent, values, default, width):
        cb = ctk.CTkComboBox(
            parent, values=values, width=width, height=38,
            fg_color=DS.WHITE, button_color=DS.G500,
            border_color=DS.G400, border_width=2,
            dropdown_fg_color=DS.WHITE,
            dropdown_hover_color=DS.G100,
            font=_font(14), text_color=DS.N800
        )
        cb.set(default)
        return cb

    def _radio_pill(self, parent, text, variable, value, cmd=None):
        return ctk.CTkRadioButton(
            parent, text=text, variable=variable, value=value,
            text_color=DS.N800, fg_color=DS.G500,
            hover_color=DS.G400,
            font=_font(15),
            command=cmd
        )

    # ══════════════════════════════════════════════════════
    #  CALENDAR
    # ══════════════════════════════════════════════════════
    def _build_calendar_grid(self):
        for w in self.days_grid_frame.winfo_children():
            w.destroy()

        self.cal_month_label.configure(
            text=f"{self.view_date.strftime('%B')} {self.view_date.year}"
        )

        for i, day_name in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            ctk.CTkLabel(
                self.days_grid_frame, text=day_name,
                width=40, font=_font(11, "bold"), text_color=DS.G600
            ).grid(row=0, column=i, padx=1, pady=(2, 4))

        cal   = calendar.monthcalendar(self.view_date.year, self.view_date.month)
        today = datetime.now().date()

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                cur  = datetime(self.view_date.year, self.view_date.month, day).date()
                past = cur < today
                sel  = (
                    day == self.selected_date.day
                    and self.view_date.month == self.selected_date.month
                    and self.view_date.year  == self.selected_date.year
                )
                is_today = cur == today

                fg = DS.G500 if sel else DS.N100 if past else (DS.G100 if is_today else "transparent")
                tc = DS.WHITE if sel else DS.N400 if past else (DS.G600 if is_today else DS.N800)
                hv = DS.G400 if sel else DS.N100 if past else DS.G200

                btn = ctk.CTkButton(
                    self.days_grid_frame,
                    text=str(day), width=40, height=38,
                    corner_radius=8, anchor="center",
                    fg_color=fg, text_color=tc, hover_color=hv,
                    font=_font(13, "bold" if sel or is_today else "normal"),
                    border_width=2 if is_today and not sel else 0,
                    border_color=DS.G400,
                    state="disabled" if past else "normal",
                    command=(lambda d=day: self._select_day(d)) if not past else lambda: None
                )
                btn.grid(row=r+1, column=c, padx=1, pady=1, sticky="nsew")
                self.days_grid_frame.grid_rowconfigure(r+1, weight=1)
                self.days_grid_frame.grid_columnconfigure(c, weight=1)

    def _select_day(self, day):
        self.selected_date = self.view_date.replace(day=day)
        self._build_calendar_grid()

    def _prev_month(self):
        m, y = self.view_date.month - 1, self.view_date.year
        if m == 0:
            m, y = 12, y - 1
        self.view_date = self.view_date.replace(year=y, month=m, day=1)
        self._build_calendar_grid()

    def _next_month(self):
        m, y = self.view_date.month + 1, self.view_date.year
        if m == 13:
            m, y = 1, y + 1
        self.view_date = self.view_date.replace(year=y, month=m, day=1)
        self._build_calendar_grid()

    def _toggle_recurring(self):
        if self.recurring_var.get():
            self.recurring_frame.pack(fill="x", padx=24, pady=(6, 0))
        else:
            self.recurring_frame.pack_forget()

    def _on_spray_type_change(self):
        mapping = {"Fertilizer": "Container 1", "Pesticide": "Container 2"}
        self.cont_var.set(mapping.get(self.spray_var.get(), "Container 1"))

    # ══════════════════════════════════════════════════════
    #  TIME CONVERSION
    # ══════════════════════════════════════════════════════
    def _convert_to_24h(self, h12, ampm):
        h = int(h12)
        if ampm == "AM":
            return 0 if h == 12 else h
        return 12 if h == 12 else h + 12

    def _convert_to_12h(self, h24):
        h = int(h24)
        if h == 0:   return 12, "AM"
        if h < 12:   return h,  "AM"
        if h == 12:  return 12, "PM"
        return h - 12, "PM"

    def _is_datetime_in_past(self, date_str, time_str):
        try:
            y, mo, d = map(int, date_str.split('-'))
            h, mi    = map(int, time_str.split(':'))
            return datetime(y, mo, d, h, mi) < datetime.now()
        except Exception:
            return False

    # ══════════════════════════════════════════════════════
    #  SCHEDULE CREATION
    # ══════════════════════════════════════════════════════
    def _handle_create(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        h24      = self._convert_to_24h(self.hour_cb.get(), self.ampm_cb.get())
        time_str = f"{h24:02d}:{self.min_cb.get()}"

        if self._is_datetime_in_past(date_str, time_str):
            self._show_invalid_time_dialog()
            return

        try:
            vol = float(self.vol_entry.get())
            if vol <= 0:
                messagebox.showerror("Error", "Volume must be greater than 0 mL")
                return

            if self.recurring_var.get():
                if not self.interval_entry.get() or not self.count_entry.get():
                    messagebox.showerror("Error", "Fill in interval and count for recurring schedule")
                    return

                interval = int(self.interval_entry.get())
                count    = int(self.count_entry.get())

                if interval < 1:
                    messagebox.showerror("Error", "Interval must be at least 1 day")
                    return
                if count < 2:
                    messagebox.showerror("Error", "Count must be at least 2 for recurring schedules")
                    return

                schedules = self.scheduler.create_recurring_schedules(
                    date_str, interval, count, time_str,
                    self.spray_var.get(), self.cont_var.get(), vol
                )
                self._show_success_toast(f"Created {len(schedules)} recurring schedules")
                if self.dashboard_callback:
                    for s in schedules:
                        self.dashboard_callback(s)
            else:
                new_task = self.scheduler.create_schedule(
                    date_str, time_str, self.spray_var.get(), self.cont_var.get(), vol
                )
                h12, ap = self._convert_to_12h(h24)
                disp = f"{h12:02d}:{self.min_cb.get()} {ap}"
                self._show_success_toast(f"Schedule created for {date_str} at {disp}")
                if self.dashboard_callback:
                    self.dashboard_callback(new_task)

            self.refresh_schedule_list()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create schedule: {e}")
            self.logger.log_error(f"Schedule creation error: {e}")

    # ══════════════════════════════════════════════════════
    #  SCHEDULE LIST
    # ══════════════════════════════════════════════════════
    def refresh_schedule_list(self):
        for w in self.schedule_list.winfo_children():
            w.destroy()

        schedules = self.scheduler.data_store.get_active_schedules()

        if not schedules:
            empty = ctk.CTkFrame(self.schedule_list, fg_color="transparent")
            empty.pack(expand=True, pady=60)
            ctk.CTkLabel(
                empty, text="🌿", font=_font(36)
            ).pack()
            ctk.CTkLabel(
                empty, text="No active schedules",
                font=_font(15, "bold"), text_color=DS.N400
            ).pack(pady=(6, 2))
            ctk.CTkLabel(
                empty, text="Create one using the form on the left",
                font=_font(12), text_color=DS.N400
            ).pack()
            return

        for sc in sorted(schedules, key=lambda x: f"{x['date']} {x['time']}"):
            self._create_card(sc)

    def _create_card(self, sc):
        card = ctk.CTkFrame(
            self.schedule_list,
            fg_color=DS.WHITE, corner_radius=12,
            border_width=1, border_color=DS.N200
        )
        card.pack(fill="x", padx=12, pady=6)

        # ── Card header strip
        strip = ctk.CTkFrame(card, fg_color=DS.G500, corner_radius=10, height=5)
        strip.pack(fill="x", padx=3, pady=(3, 0))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=10)
        body.grid_columnconfigure(0, weight=1)

        # Date/time row
        tp    = sc['time'].split(':')
        h12, ap = self._convert_to_12h(int(tp[0]))
        disp_t  = f"{h12:02d}:{tp[1]} {ap}"

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_row,
            text=f"📅  {sc['date']}  ·  🕐 {disp_t}",
            font=_font(17, "bold"), text_color=DS.G800, anchor="w"
        ).grid(row=0, column=0, sticky="w")

        # Status badge
        status_colors = {
            "pending":   (DS.AMBER,  "#FFF8E1"),
            "completed": (DS.G500,   DS.G100),
            "cancelled": (DS.RED,    "#FFF0F0"),
        }
        st = sc.get('status', 'pending').lower()
        sc_color, sc_bg = status_colors.get(st, (DS.N600, DS.N100))
        badge = ctk.CTkFrame(top_row, fg_color=sc_bg, corner_radius=10)
        badge.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            badge, text=st.capitalize(),
            font=_font(13, "bold"), text_color=sc_color
        ).pack(padx=10, pady=2)

        # Divider
        ctk.CTkFrame(body, fg_color=DS.N200, height=1).grid(
            row=1, column=0, sticky="ew", pady=8)

        # Info grid
        info_frame = ctk.CTkFrame(body, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="ew")
        info_frame.grid_columnconfigure((0,1), weight=1)

        vol  = sc.get('volume_ml', 1000)
        dur  = self.scheduler.calculate_spray_duration(vol)
        resc = sc.get('reschedule_count', 0)

        pairs = [
            ("Type",       sc['spray_type']),
            ("Container",  sc['container']),
            ("Volume",     f"{vol} mL"),
            ("Duration",   f"{dur:.1f}s"),
            ("Reschedules",f"{resc}/3"),
        ]

        for idx, (label, val) in enumerate(pairs):
            col = idx % 2
            row = idx // 2 + 3
            cell = ctk.CTkFrame(info_frame, fg_color=DS.G50, corner_radius=6)
            cell.grid(row=row, column=col, sticky="ew", padx=(0 if col==0 else 4, 0), pady=2)
            info_frame.grid_rowconfigure(row, weight=0)
            ctk.CTkLabel(cell, text=label, font=_font(12, "bold"),
                         text_color=DS.N400).pack(anchor="w", padx=8, pady=(5, 0))
            ctk.CTkLabel(cell, text=val, font=_font(16, "bold"),
                         text_color=DS.N800).pack(anchor="w", padx=8, pady=(0, 5))

        # Buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.grid(row=10, column=0, sticky="ew", pady=(10, 0))

        ctk.CTkButton(
            btn_row, text="✎  Reschedule",
            fg_color=DS.AMBER, hover_color=DS.AMBER_D,
            width=140, height=38, corner_radius=8,
            font=_font(15, "bold"), text_color=DS.WHITE,
            command=lambda s=sc: self._open_reschedule_dialog(s)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="✕  Cancel",
            fg_color=DS.RED, hover_color=DS.RED_D,
            width=120, height=38, corner_radius=8,
            font=_font(15, "bold"), text_color=DS.WHITE,
            command=lambda s=sc: self._cancel_one(s['id'])
        ).pack(side="left")

    # ══════════════════════════════════════════════════════
    #  DIALOGS
    # ══════════════════════════════════════════════════════
    def _center_dialog(self, dlg, w, h):
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth()  // 2) - (w // 2)
        y = (dlg.winfo_screenheight() // 2) - (h // 2)
        dlg.geometry(f"{w}x{h}+{x}+{y}")

    def _show_invalid_time_dialog(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 380, 210)

        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        # Top accent bar
        ctk.CTkFrame(outer, fg_color=DS.AMBER, height=4, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))

        icon_bg = ctk.CTkFrame(hdr, fg_color=DS.AMBER, width=44, height=44, corner_radius=22)
        icon_bg.pack(side="left", padx=(0, 12))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="!", font=_font(22, "bold"),
                     text_color=DS.WHITE).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(hdr, text="Invalid Time",
                     font=_font(17, "bold"), text_color=DS.N800).pack(side="left")

        ctk.CTkLabel(inner, text="You can't schedule sprays in the past.",
                     font=_font(13), text_color=DS.N600, anchor="w").pack(anchor="w")
        ctk.CTkLabel(inner, text="Please select a future date and time.",
                     font=_font(13), text_color=DS.N600, anchor="w").pack(anchor="w", pady=(2, 16))

        ctk.CTkButton(
            inner, text="Got it", command=dlg.destroy,
            fg_color=DS.AMBER, hover_color=DS.AMBER_D,
            height=40, width=130, corner_radius=8,
            font=_font(14, "bold"), text_color=DS.WHITE
        ).pack(anchor="center")

    def _show_success_toast(self, message, duration=3000):
        toast = ctk.CTkToplevel(self)
        toast.withdraw()
        toast.overrideredirect(True)

        frame = ctk.CTkFrame(toast, fg_color=DS.G800, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=10)

        ctk.CTkLabel(inner, text="✓", font=_font(18, "bold"),
                     text_color=DS.G200, width=24).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(inner, text=message, font=_font(13, "bold"),
                     text_color=DS.WHITE, anchor="w").pack(side="left", fill="x", expand=True)

        toast.update_idletasks()
        sw, sh = toast.winfo_screenwidth(), toast.winfo_screenheight()
        tw, th = 360, 48
        toast.geometry(f"{tw}x{th}+{sw - tw - 20}+20")
        toast.deiconify()
        toast.lift()
        toast.attributes('-topmost', True)
        toast.after(duration, toast.destroy)

    def _show_cancel_confirmation(self, callback):
        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 380, 215)

        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        ctk.CTkFrame(outer, fg_color=DS.RED, height=4, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))

        icon_bg = ctk.CTkFrame(hdr, fg_color="#FEE2E2", width=44, height=44, corner_radius=22)
        icon_bg.pack(side="left", padx=(0, 12))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="⚠", font=_font(20),
                     text_color=DS.RED).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(hdr, text="Cancel Schedule",
                     font=_font(17, "bold"), text_color=DS.N800).pack(side="left")

        ctk.CTkLabel(inner, text="This will cancel this active spray schedule.",
                     font=_font(13), text_color=DS.N600).pack(anchor="w")
        ctk.CTkLabel(inner, text="This action cannot be undone.",
                     font=_font(12), text_color=DS.RED).pack(anchor="w", pady=(2, 16))

        bf = ctk.CTkFrame(inner, fg_color="transparent")
        bf.pack(fill="x")
        bf.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(bf, text="Keep", command=dlg.destroy,
                      fg_color=DS.N100, text_color=DS.N800, hover_color=DS.N200,
                      height=42, corner_radius=8, font=_font(14)
                      ).grid(row=0, column=0, sticky="ew", padx=(0,5))

        def _do():
            dlg.destroy()
            callback()

        ctk.CTkButton(bf, text="Cancel Schedule", command=_do,
                      fg_color=DS.RED, hover_color=DS.RED_D, text_color=DS.WHITE,
                      height=42, corner_radius=8, font=_font(14, "bold")
                      ).grid(row=0, column=1, sticky="ew", padx=(5,0))

    # ── RESCHEDULE DIALOG ─────────────────────────────────
    def _open_reschedule_dialog(self, schedule):
        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 500, 700)

        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        ctk.CTkFrame(outer, fg_color=DS.G500, height=4, corner_radius=0).pack(fill="x")

        # Title bar
        title_bar = ctk.CTkFrame(outer, fg_color="transparent")
        title_bar.pack(fill="x", padx=20, pady=(14, 8))
        ctk.CTkLabel(title_bar, text="✎  Reschedule",
                     font=_font(18, "bold"), text_color=DS.G800).pack(side="left")

        scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=DS.G200,
            scrollbar_button_hover_color=DS.G400,
        )
        scroll.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # ── DATE ──
        ctk.CTkLabel(scroll, text="Select New Date",
                     font=_font(13, "bold"), text_color=DS.G800).pack(anchor="w", padx=16, pady=(8, 6))

        y_, mo_, d_ = map(int, schedule['date'].split('-'))
        sel_date = {"date": datetime(y_, mo_, d_)}

        cal_card = ctk.CTkFrame(scroll, fg_color=DS.G100, corner_radius=12,
                                 border_width=1, border_color=DS.G200)
        cal_card.pack(fill="x", padx=16)

        nav = ctk.CTkFrame(cal_card, fg_color="transparent")
        nav.pack(fill="x", padx=12, pady=(10, 4))
        nav.grid_columnconfigure(1, weight=1)

        mo_lbl = ctk.CTkLabel(nav, text="", font=_font(14, "bold"), text_color=DS.G800)
        mo_lbl.grid(row=0, column=1)

        days_grid = ctk.CTkFrame(cal_card, fg_color="transparent")
        days_grid.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        def build_cal():
            for w in days_grid.winfo_children():
                w.destroy()
            mo_lbl.configure(text=f"{sel_date['date'].strftime('%B')} {sel_date['date'].year}")
            for i, dn in enumerate(["Su","Mo","Tu","We","Th","Fr","Sa"]):
                ctk.CTkLabel(days_grid, text=dn, width=38,
                             font=_font(10, "bold"), text_color=DS.G600).grid(
                    row=0, column=i, padx=1, pady=(2,4))

            cal_m = calendar.monthcalendar(sel_date['date'].year, sel_date['date'].month)
            today = datetime.now().date()

            for r, week in enumerate(cal_m):
                for c, dn in enumerate(week):
                    if dn == 0:
                        continue
                    cur  = datetime(sel_date['date'].year, sel_date['date'].month, dn).date()
                    past = cur < today
                    seld = (dn == sel_date['date'].day)
                    itd  = cur == today

                    fg = DS.G500 if seld else DS.N100 if past else (DS.G100 if itd else "transparent")
                    tc = DS.WHITE if seld else DS.N400 if past else (DS.G600 if itd else DS.N800)
                    hv = DS.G400 if seld else DS.N100 if past else DS.G200

                    b = ctk.CTkButton(
                        days_grid, text=str(dn), width=38, height=36,
                        corner_radius=8, anchor="center",
                        fg_color=fg, text_color=tc, hover_color=hv,
                        font=_font(12, "bold" if seld else "normal"),
                        state="disabled" if past else "normal",
                        command=(lambda d=dn: (sel_date.__setitem__('date', sel_date['date'].replace(day=d)), build_cal())) if not past else lambda: None
                    )
                    b.grid(row=r+1, column=c, padx=1, pady=1, sticky="nsew")
                    days_grid.grid_rowconfigure(r+1, weight=1)
                for col in range(7):
                    days_grid.grid_columnconfigure(col, weight=1)

        def prev_mo():
            m, y = sel_date['date'].month-1, sel_date['date'].year
            if m == 0: m, y = 12, y-1
            sel_date['date'] = sel_date['date'].replace(year=y, month=m, day=1)
            build_cal()

        def next_mo():
            m, y = sel_date['date'].month+1, sel_date['date'].year
            if m == 13: m, y = 1, y+1
            sel_date['date'] = sel_date['date'].replace(year=y, month=m, day=1)
            build_cal()

        ctk.CTkButton(nav, text="‹", width=32, height=32, corner_radius=16,
                      fg_color=DS.G500, hover_color=DS.G600,
                      font=_font(15, "bold"), command=prev_mo
                      ).grid(row=0, column=0, padx=(0,6))
        ctk.CTkButton(nav, text="›", width=32, height=32, corner_radius=16,
                      fg_color=DS.G500, hover_color=DS.G600,
                      font=_font(15, "bold"), command=next_mo
                      ).grid(row=0, column=2, padx=(6,0))
        build_cal()

        # ── CONTAINER ──
        ctk.CTkLabel(scroll, text="Container",
                     font=_font(13, "bold"), text_color=DS.G800).pack(anchor="w", padx=16, pady=(16, 6))

        new_cont_var = ctk.StringVar(value=schedule.get('container', 'Container 1'))
        cont_row = ctk.CTkFrame(scroll, fg_color="transparent")
        cont_row.pack(anchor="w", padx=16)
        for val in ["Container 1", "Container 2"]:
            ctk.CTkRadioButton(
                cont_row, text=val, variable=new_cont_var, value=val,
                text_color=DS.N800, fg_color=DS.G500, hover_color=DS.G400,
                font=_font(14)
            ).pack(side="left", padx=(0, 16))

        # ── VOLUME ──
        ctk.CTkLabel(scroll, text="Spray Volume (mL)",
                     font=_font(13, "bold"), text_color=DS.G800).pack(anchor="w", padx=16, pady=(16, 6))

        vol_row = ctk.CTkFrame(scroll, fg_color="transparent")
        vol_row.pack(anchor="w", padx=16)

        new_vol_entry = ctk.CTkEntry(
            vol_row, width=110, height=38,
            fg_color=DS.WHITE, border_color=DS.G400, border_width=2,
            font=_font(14), text_color=DS.N800
        )
        new_vol_entry.insert(0, str(schedule.get('volume_ml', 1000)))
        new_vol_entry.pack(side="left")
        ctk.CTkLabel(vol_row, text="mL", font=_font(13, "bold"),
                     text_color=DS.N600).pack(side="left", padx=(8, 0))

        # ── TIME ──
        ctk.CTkLabel(scroll, text="Select New Time",
                     font=_font(13, "bold"), text_color=DS.G800).pack(anchor="w", padx=16, pady=(16, 6))

        tp   = schedule['time'].split(':')
        h12, ap = self._convert_to_12h(int(tp[0]))
        tf = ctk.CTkFrame(scroll, fg_color="transparent")
        tf.pack(anchor="w", padx=16)

        new_hr  = self._dropdown(tf, [f"{i:02d}" for i in range(1,13)], f"{h12:02d}", 78)
        new_hr.pack(side="left")
        ctk.CTkLabel(tf, text=":", font=_font(18,"bold"), text_color=DS.N800).pack(side="left", padx=4)
        new_mn  = self._dropdown(tf, [f"{i:02d}" for i in range(0,60,5)], tp[1], 78)
        new_mn.pack(side="left")
        new_ap  = self._dropdown(tf, ["AM","PM"], ap, 76)
        new_ap.pack(side="left", padx=(10,0))

        # ── ACTION BUTTONS ──
        bf = ctk.CTkFrame(scroll, fg_color="transparent")
        bf.pack(fill="x", padx=16, pady=(16, 8))

        def confirm():
            nd = sel_date['date'].strftime("%Y-%m-%d")
            h24 = self._convert_to_24h(new_hr.get(), new_ap.get())
            nt  = f"{h24:02d}:{new_mn.get()}"
            if self._is_datetime_in_past(nd, nt):
                self._show_invalid_time_dialog()
                return

            # Validate volume
            try:
                new_vol = float(new_vol_entry.get())
                if new_vol <= 0:
                    messagebox.showerror("Error", "Volume must be greater than 0 mL")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid volume value")
                return

            ok, msg, affected = self.reschedule_mgr.reschedule(
                schedule['id'], nd, nt,
                container=new_cont_var.get(),
                volume_ml=new_vol
            )
            if ok:
                h12d, apd = self._convert_to_12h(h24)
                disp = f"{h12d:02d}:{new_mn.get()} {apd}"
                m = f"Rescheduled to {nd} at {disp}"
                if affected:
                    m += f" ({len(affected)} schedule(s) adjusted)"
                self._show_success_toast(m)
                dlg.destroy()
                self.refresh_schedule_list()
            else:
                messagebox.showerror("Error", msg)
                dlg.destroy()
                self.refresh_schedule_list()

        ctk.CTkButton(bf, text="Cancel", command=dlg.destroy,
                      fg_color=DS.N100, text_color=DS.N800, hover_color=DS.N200,
                      height=42, corner_radius=8, font=_font(13), width=130
                      ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(bf, text="✓  Confirm Reschedule", command=confirm,
                      fg_color=DS.G500, hover_color=DS.G600, text_color=DS.WHITE,
                      height=42, corner_radius=8, font=_font(13, "bold"), width=200
                      ).pack(side="right")

    # ── CANCEL ONE ────────────────────────────────────────
    def _cancel_one(self, sid):
        def do():
            self.reschedule_mgr.cancel_schedule(sid)
            self._show_success_toast("Schedule cancelled")
            self.refresh_schedule_list()
        self._show_cancel_confirmation(do)

    # ── CANCEL ALL ────────────────────────────────────────
    def _cancel_all(self):
        schedules = self.scheduler.data_store.get_active_schedules()
        if not schedules:
            messagebox.showinfo("Info", "No active schedules to cancel")
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.overrideredirect(True)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        self._center_dialog(dlg, 400, 265)

        outer = ctk.CTkFrame(dlg, fg_color=DS.WHITE, corner_radius=16,
                              border_width=1, border_color=DS.N200)
        outer.pack(fill="both", expand=True, padx=2, pady=2)
        ctk.CTkFrame(outer, fg_color=DS.RED, height=4, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=20)

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))

        icon_bg = ctk.CTkFrame(hdr, fg_color="#FEE2E2", width=50, height=50, corner_radius=25)
        icon_bg.pack(side="left", padx=(0, 14))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="⚠", font=_font(24),
                     text_color=DS.RED).place(relx=.5, rely=.5, anchor="center")

        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="Cancel All Schedules",
                     font=_font(17, "bold"), text_color=DS.N800).pack(anchor="w")
        ctk.CTkLabel(title_col, text=f"{len(schedules)} schedule(s) will be removed",
                     font=_font(12), text_color=DS.N400).pack(anchor="w")

        ctk.CTkLabel(inner, text="This will permanently cancel ALL active spray schedules.",
                     font=_font(13), text_color=DS.N600).pack(anchor="w")
        ctk.CTkLabel(inner, text="This action cannot be undone.",
                     font=_font(12), text_color=DS.RED).pack(anchor="w", pady=(2, 18))

        bf = ctk.CTkFrame(inner, fg_color="transparent")
        bf.pack(fill="x")
        bf.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(bf, text="Keep All", command=dlg.destroy,
                      fg_color=DS.N100, text_color=DS.N800, hover_color=DS.N200,
                      height=44, corner_radius=8, font=_font(14)
                      ).grid(row=0, column=0, sticky="ew", padx=(0,5))

        def do_all():
            self.reschedule_mgr.cancel_all_schedules()
            dlg.destroy()
            self._show_success_toast("All schedules cancelled")
            self.refresh_schedule_list()

        ctk.CTkButton(bf, text="Cancel All", command=do_all,
                      fg_color=DS.RED, hover_color=DS.RED_D, text_color=DS.WHITE,
                      height=44, corner_radius=8, font=_font(14, "bold")
                      ).grid(row=0, column=1, sticky="ew", padx=(5,0))