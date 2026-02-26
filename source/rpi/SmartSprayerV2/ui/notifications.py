# notifications.py
# Automated Sprayer System – Notifications (Modernized)

import customtkinter as ctk
from datetime import datetime
import threading
import time

from core.data_store import get_recipients

# ══════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════
GREEN       = "#4CAF50"
DARK_GREEN  = "#1B5E20"
BLUE        = "#2196F3"
ORANGE      = "#FF9800"
RED         = "#F44336"
GRAY        = "#616161"
LIGHT_BG    = "#EAF3F0"
WHITE       = "#FFFFFF"

TAB_ACTIVE_BG   = "#4CAF50"
TAB_ACTIVE_TEXT = "white"
TAB_IDLE_BG     = "#D6EEE0"
TAB_IDLE_TEXT   = "#1B5E20"


class NotificationsPanel(ctk.CTkFrame):

    def __init__(self, parent, scheduler, data_store, hardware):
        super().__init__(parent)

        self.scheduler  = scheduler
        self.data_store = data_store
        self.hardware   = hardware

        self.last_tank1 = 0
        self.last_tank2 = 0

        self.configure(fg_color="#F3F8F6")

        self._build_ui()
        self._start_clock()

        self.running = True
        threading.Thread(target=self._fetch_hardware_loop, daemon=True).start()
        self.after(500, self._main_update_loop)

    # ══════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════

    def _card(self, parent, **kwargs):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=18, **kwargs)
        card.pack_propagate(False)
        return card

    def _section_title(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=DARK_GREEN
        ).pack(anchor="w", padx=24, pady=(24, 14))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color="#E8F5E9", height=3, corner_radius=0).pack(
            fill="x", padx=20, pady=0
        )

    # ══════════════════════════════════════════════════════
    # UI BUILD
    # ══════════════════════════════════════════════════════

    def _build_ui(self):

        # ── PAGE HEADER ──────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(side="left", fill="y", padx=30)

        tabs = ctk.CTkFrame(inner, fg_color="transparent")
        tabs.pack(side="left", fill="y")

        self.tab_status_btn = ctk.CTkButton(
            tabs,
            text="System & Status",
            font=ctk.CTkFont(size=32, weight="bold"),
            fg_color=TAB_ACTIVE_BG,
            text_color=TAB_ACTIVE_TEXT,
            hover_color="#388E3C",
            corner_radius=14,
            width=340, height=70,
            command=self._show_status_tab
        )
        self.tab_status_btn.pack(side="left", padx=(0, 16), pady=20)

        self.tab_sched_btn = ctk.CTkButton(
            tabs,
            text="Schedules",
            font=ctk.CTkFont(size=32, weight="bold"),
            fg_color=TAB_IDLE_BG,
            text_color=TAB_IDLE_TEXT,
            hover_color="#C8E6C9",
            corner_radius=14,
            width=340, height=70,
            command=self._show_schedules_tab
        )
        self.tab_sched_btn.pack(side="left", pady=20)

        # Accent underline
        ctk.CTkFrame(self, fg_color=GREEN, height=5, corner_radius=0).pack(fill="x")

        # ── CONTENT ──────────────────────────────────────
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self._build_status_view()
        self._build_schedules_view()
        self._show_status_tab()

    # ══════════════════════════════════════════════════════
    # STATUS VIEW
    # ══════════════════════════════════════════════════════

    def _build_status_view(self):

        self.status_view = ctk.CTkFrame(self.content_container, fg_color="transparent")

        top = ctk.CTkFrame(self.status_view, fg_color="transparent")
        top.pack(fill="both", expand=True, padx=30, pady=20)
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_rowconfigure(0, weight=1)

        # ── LEFT COLUMN ──────────────────────────────────
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(1, weight=1)

        # System Status card
        sys_card = self._card(left)
        sys_card.pack(fill="x", pady=(0, 14))

        self._section_title(sys_card, "System Status")
        self._divider(sys_card)

        status_inner = ctk.CTkFrame(sys_card, fg_color="transparent")
        status_inner.pack(pady=24)

        self.status_pill = ctk.CTkFrame(
            status_inner,
            fg_color="transparent",
            corner_radius=999,
        )
        self.status_pill.pack()

        self.system_status = ctk.CTkLabel(
            self.status_pill,
            text="● IDLE",
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=GREEN,
            padx=40, pady=18
        )
        self.system_status.pack()

        self.next_spray = ctk.CTkLabel(
            status_inner,
            text="Next Spray: --",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=GRAY
        )
        self.next_spray.pack(pady=(16, 0))

        # Tank Status card
        tank_card = self._card(left)
        tank_card.pack(fill="both", expand=True)

        self._section_title(tank_card, "Tank Status")
        self._divider(tank_card)

        tank_row = ctk.CTkFrame(tank_card, fg_color="transparent")
        tank_row.pack(fill="both", expand=True, padx=16, pady=16)

        self._tank_block(tank_row, "Container 1", 1)
        self._tank_block(tank_row, "Container 2", 2)

        # ── RIGHT COLUMN — MESSAGING ─────────────────────
        msg_card = self._card(top)
        msg_card.grid(row=0, column=1, sticky="nsew")

        self._section_title(msg_card, "Messaging Status")
        self._divider(msg_card)

        signal_row = ctk.CTkFrame(msg_card, fg_color="transparent")
        signal_row.pack(fill="x", padx=24, pady=(14, 8))

        self.signal = ctk.CTkLabel(
            signal_row,
            text="Signal Strength: Good",
            font=ctk.CTkFont(size=30),
            text_color=GRAY
        )
        self.signal.pack(side="left", padx=8)

        self.message_list = ctk.CTkScrollableFrame(
            msg_card,
            fg_color=LIGHT_BG,
            corner_radius=12
        )
        self.message_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_recipients()

    # ══════════════════════════════════════════════════════
    # SCHEDULES VIEW
    # ══════════════════════════════════════════════════════

    def _build_schedules_view(self):

        self.schedules_view = ctk.CTkFrame(self.content_container, fg_color="transparent")

        bottom = ctk.CTkFrame(self.schedules_view, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=30, pady=20)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)

        # Rescheduled
        resched_card = self._card(bottom)
        resched_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self._section_title(resched_card, "Rescheduled Schedules")
        self._divider(resched_card)

        self.resched = ctk.CTkScrollableFrame(
            resched_card, fg_color=LIGHT_BG, corner_radius=12
        )
        self.resched.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Cancelled
        cancel_card = self._card(bottom)
        cancel_card.grid(row=0, column=1, sticky="nsew")

        self._section_title(cancel_card, "Cancelled Schedules")
        self._divider(cancel_card)

        self.cancel = ctk.CTkScrollableFrame(
            cancel_card, fg_color=LIGHT_BG, corner_radius=12
        )
        self.cancel.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    # ══════════════════════════════════════════════════════
    # TAB SWITCHING
    # ══════════════════════════════════════════════════════

    def _show_status_tab(self):
        self.schedules_view.pack_forget()
        self.status_view.pack(fill="both", expand=True)
        self.tab_status_btn.configure(fg_color=TAB_ACTIVE_BG, text_color=TAB_ACTIVE_TEXT)
        self.tab_sched_btn.configure(fg_color=TAB_IDLE_BG,    text_color=TAB_IDLE_TEXT)

    def _show_schedules_tab(self):
        self.status_view.pack_forget()
        self.schedules_view.pack(fill="both", expand=True)
        self.tab_sched_btn.configure(fg_color=TAB_ACTIVE_BG,  text_color=TAB_ACTIVE_TEXT)
        self.tab_status_btn.configure(fg_color=TAB_IDLE_BG,   text_color=TAB_IDLE_TEXT)
        self._refresh_rescheduled_schedules()
        self._refresh_cancelled_schedules()

    # ══════════════════════════════════════════════════════
    # COMPONENTS
    # ══════════════════════════════════════════════════════

    def _tank_block(self, parent, title, idx):

        block = ctk.CTkFrame(parent, fg_color=LIGHT_BG, corner_radius=14)
        block.pack(side="left", expand=True, fill="both", padx=8)

        inner = ctk.CTkFrame(block, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=DARK_GREEN
        ).pack(pady=(0, 14))

        pct_frame = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=999)
        pct_frame.pack()

        percent = ctk.CTkLabel(
            pct_frame,
            text="0%",
            font=ctk.CTkFont(size=58, weight="bold"),
            text_color=RED,
            padx=30, pady=20
        )
        percent.pack()

        status = ctk.CTkLabel(
            inner,
            text="● CRITICAL",
            font=ctk.CTkFont(size=32),
            text_color=RED
        )
        status.pack(pady=(12, 0))

        if idx == 1:
            self.tank1_lbl    = percent
            self.tank1_status = status
            self.tank1_frame  = pct_frame
        else:
            self.tank2_lbl    = percent
            self.tank2_status = status
            self.tank2_frame  = pct_frame

    def _recipient(self, name, phone, status="Sent"):

        row = ctk.CTkFrame(self.message_list, fg_color=WHITE, corner_radius=12)
        row.pack(fill="x", padx=8, pady=8)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="y", padx=18, pady=14)

        ctk.CTkLabel(
            left,
            text=name,
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=DARK_GREEN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=phone,
            font=ctk.CTkFont(size=28),
            text_color=GRAY
        ).pack(anchor="w")

        ctk.CTkLabel(
            row,
            text=f"✓  {status}",
            font=ctk.CTkFont(size=28, weight="bold"),
            fg_color="#E8F5E9",
            text_color=GREEN,
            corner_radius=10,
            padx=20, pady=10
        ).pack(side="right", padx=18)

    def _schedule_item(self, parent, schedule_data):

        item = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=12)
        item.pack(fill="x", padx=8, pady=8)

        try:
            dt = datetime.strptime(
                f"{schedule_data['date']} {schedule_data['time']}", "%Y-%m-%d %H:%M"
            )
            datetime_text = f"{dt.strftime('%b %d, %Y')}  at  {dt.strftime('%I:%M %p')}"
        except Exception:
            datetime_text = f"{schedule_data['date']} {schedule_data['time']}"

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(14, 8))

        ctk.CTkLabel(
            top,
            text=f"🕐  {datetime_text}",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=DARK_GREEN
        ).pack(side="left")

        spray_type = schedule_data.get('spray_type', 'Spray')
        badge_color = BLUE if spray_type == 'Fertilizer' else ORANGE

        ctk.CTkLabel(
            top,
            text=spray_type,
            fg_color=badge_color,
            text_color="white",
            corner_radius=10,
            font=ctk.CTkFont(size=26, weight="bold"),
            padx=18, pady=9
        ).pack(side="right")

        ctk.CTkFrame(item, fg_color="#F0F0F0", height=2).pack(fill="x", padx=20)

        details = ctk.CTkFrame(item, fg_color="transparent")
        details.pack(anchor="w", padx=20, pady=(10, 14))

        ctk.CTkLabel(
            details,
            text=f"Container: {schedule_data.get('container', '--')}",
            font=ctk.CTkFont(size=27),
            text_color=GRAY
        ).pack(side="left", padx=(0, 24))

        ctk.CTkLabel(
            details,
            text=f"💧  Volume: {schedule_data.get('volume_ml', '--')} ml",
            font=ctk.CTkFont(size=27),
            text_color=GRAY
        ).pack(side="left")

    def _empty_label(self, parent, text="No records"):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=32),
            text_color=GRAY
        ).pack(pady=40)

    # ══════════════════════════════════════════════════════
    # UPDATE LOOP
    # ══════════════════════════════════════════════════════

    def _fetch_hardware_loop(self):
        while self.running:
            if self.hardware:
                try:
                    v1 = self.hardware.get_tank_level_percentage(1)
                    v2 = self.hardware.get_tank_level_percentage(2)
                    if v1 is not None:
                        self.last_tank1 = v1
                    if v2 is not None:
                        self.last_tank2 = v2
                except Exception:
                    pass
            time.sleep(5)

    def _main_update_loop(self):
        if not self.running:
            return
        try:
            self._update_system()
            self._update_tanks()
            self.refresh_recipients()
            self._refresh_cancelled_schedules()
            self._refresh_rescheduled_schedules()
        except Exception as e:
            print(f"\u274c Notifications update error: {e}")
        try:
            self.after(3000, self._main_update_loop)
        except Exception:
            pass

    def _refresh_cancelled_schedules(self):
        for w in self.cancel.winfo_children():
            w.destroy()
        cancelled = self.data_store.get_cancelled_schedules()
        if not cancelled:
            self._empty_label(self.cancel)
        else:
            for s in reversed(cancelled[-10:]):
                self._schedule_item(self.cancel, s)

    def _refresh_rescheduled_schedules(self):
        for w in self.resched.winfo_children():
            w.destroy()
        rescheduled = self.data_store.get_rescheduled_schedules()
        if not rescheduled:
            self._empty_label(self.resched)
        else:
            for s in reversed(rescheduled[-10:]):
                self._schedule_item(self.resched, s)

    def _update_system(self):
        nxt = self.scheduler.get_next_schedule()
        if nxt:
            self.system_status.configure(text="● SCHEDULED", text_color=BLUE)
            try:
                dt = datetime.strptime(f"{nxt['date']} {nxt['time']}", "%Y-%m-%d %H:%M")
                display = f"Next Spray: {dt.strftime('%b %d, %Y')} at {dt.strftime('%I:%M %p')}"
            except Exception:
                display = f"Next Spray: {nxt['date']} {nxt['time']}"
            self.next_spray.configure(text=display)
        else:
            self.system_status.configure(text="● IDLE", text_color=GREEN)
            self.next_spray.configure(text="Next Spray: --")

    def _update_tanks(self):
        self._apply_tank_ui(
            self.tank1_lbl, self.tank1_status, self.tank1_frame, self.last_tank1
        )
        self._apply_tank_ui(
            self.tank2_lbl, self.tank2_status, self.tank2_frame, self.last_tank2
        )

    def _apply_tank_ui(self, lbl, status_lbl, frame, value):
        pct = int(value)
        if pct >= 60:
            color, label = GREEN,  "● OK"
        elif pct >= 30:
            color, label = ORANGE, "● LOW"
        else:
            color, label = RED,    "● CRITICAL"

        lbl.configure(text=f"{pct}%", text_color=color)
        status_lbl.configure(text=label, text_color=color)

    # ══════════════════════════════════════════════════════
    # RECIPIENT REFRESH
    # ══════════════════════════════════════════════════════

    def refresh_recipients(self):
        for w in self.message_list.winfo_children():
            w.destroy()

        recipients = get_recipients()

        if not recipients:
            self._empty_label(self.message_list, "No recipients")
            return

        for r in recipients:
            self._recipient(r.get("name", "Unknown"), r.get("phone", ""))

    # ══════════════════════════════════════════════════════
    # CLOCK
    # ══════════════════════════════════════════════════════

    def _start_clock(self):
        self._update_datetime()
        self.after(1000, self._start_clock)

    def _update_datetime(self):
        pass

    # ══════════════════════════════════════════════════════

    def cleanup(self):
        self.running = False
