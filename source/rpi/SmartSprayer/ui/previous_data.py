# previous_data.py
# Automated Sprayer System – Previous Data (Modernized)

import customtkinter as ctk
from datetime import datetime


class PreviousDataPanel(ctk.CTkFrame):

    def __init__(self, parent, data_store):
        super().__init__(parent)
        self.data_store = data_store
        self.configure(fg_color="#F3F8F6")
        self._create_widgets()
        self.refresh_data()
        self._run_clock()

    def _soft_card(self, parent, corner=16):
        return ctk.CTkFrame(parent, fg_color="#E2EFEA", corner_radius=corner)

    def _label(self, parent, text, size, weight="normal", color="#616161", **kw):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            text_color=color,
            **kw
        )

    # ══════════════════════════════════════════════════════
    # MOUSE-WHEEL SCROLL
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
            widget.bind("<MouseWheel>", _scroll,    add="+")
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

    def _create_widgets(self):

        # FILTER BAR
        filter_card = self._soft_card(self)
        filter_card.pack(fill="x", padx=30, pady=(14, 6))

        row = ctk.CTkFrame(filter_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=16)

        self._label(row, "Filter:", size=30, weight="bold").pack(side="left")

        self.filter_var = ctk.StringVar(value="All")

        pill_row = ctk.CTkFrame(row, fg_color="transparent")
        pill_row.pack(side="left", padx=10)

        for name in ["All", "Fertilizer", "Pesticide"]:
            self._radio_pill(pill_row, name)

        ctk.CTkButton(
            row,
            text="\u21bb  Refresh",
            width=200, height=62,
            corner_radius=14,
            fg_color="#2196F3",
            hover_color="#1E88E5",
            font=ctk.CTkFont(size=26, weight="bold"),
            command=self.refresh_data
        ).pack(side="right")

        # STATISTICS
        self._label(self, "Statistics:", size=32, weight="bold").pack(anchor="w", padx=30, pady=(20, 10))

        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=30)

        self.total_lbl = self._stat_card(stats_row, "Total Sprays", accent="#1B5E20")
        self.fert_lbl  = self._stat_card(stats_row, "Fertilizer",   accent="#2196F3")
        self.pest_lbl  = self._stat_card(stats_row, "Pesticide",    accent="#F4B400")

        # HISTORY HEADER
        hist_hdr = ctk.CTkFrame(self, fg_color="transparent")
        hist_hdr.pack(fill="x", padx=30, pady=(24, 8))

        self._label(hist_hdr, "History", size=32, weight="bold").pack(side="left")

        # HISTORY LIST
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self._bind_mousewheel(self.list_frame)

    def _radio_pill(self, parent, name):
        ctk.CTkRadioButton(
            parent,
            text=name,
            variable=self.filter_var,
            value=name,
            command=self.refresh_data,
            font=ctk.CTkFont(size=28),
            radiobutton_width=32,
            radiobutton_height=32,
            fg_color="#1B5E20",
            hover_color="#2E7D32",
            border_color="#1B5E20",
        ).pack(side="left", padx=12)

    def _stat_card(self, parent, title, accent="#1B5E20"):
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(side="left", expand=True, fill="x", padx=6)

        strip = ctk.CTkFrame(outer, fg_color=accent, corner_radius=12, height=6)
        strip.pack(fill="x")
        strip.pack_propagate(False)

        card = self._soft_card(outer, corner=12)
        card.pack(fill="x")

        self._label(card, title, size=26, color="#616161").pack(pady=(16, 6))

        value_lbl = ctk.CTkLabel(
            card, text="0",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#1B5E20"
        )
        value_lbl.pack(pady=(0, 16))

        return value_lbl

    def refresh_data(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        history     = self.data_store.get_history()
        all_history = history.copy()

        f = self.filter_var.get()
        if f != "All":
            history = [h for h in history if h["spray_type"] == f]

        self.total_lbl.configure(text=str(len(all_history)))
        self.fert_lbl.configure(text=str(len([h for h in all_history if h["spray_type"] == "Fertilizer"])))
        self.pest_lbl.configure(text=str(len([h for h in all_history if h["spray_type"] == "Pesticide"])))

        if not history:
            self._empty_state()
            return

        for item in reversed(history):
            self._history_row(item)

        # Re-bind after new children are added
        self._bind_mousewheel(self.list_frame)

    def _empty_state(self):
        frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True, pady=60)
        self._label(frame, "No spray records found for this filter.", size=28, color="#616161").pack()

    def _history_row(self, item):
        row = self._soft_card(self.list_frame)
        row.pack(fill="x", pady=8)

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(16, 8))

        try:
            dt = datetime.strptime(f"{item['date']} {item['time']}", "%Y-%m-%d %H:%M")
            display = dt.strftime("%b %d, %Y  at  %I:%M %p")
        except Exception:
            display = f"{item['date']} {item['time']}"

        self._label(top, f"\U0001f550  {display}", size=28, weight="bold", color="#1B5E20").pack(side="left")

        badge_color = "#2196F3" if item["spray_type"] == "Fertilizer" else "#F4B400"
        ctk.CTkLabel(
            top, text=item["spray_type"],
            fg_color=badge_color, text_color="white",
            corner_radius=10, padx=22, pady=10,
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(side="right")

        ctk.CTkFrame(row, fg_color="#C8DDD4", height=2).pack(fill="x", padx=24)

        bottom = ctk.CTkFrame(row, fg_color="transparent")
        bottom.pack(fill="x", padx=24, pady=(10, 18))

        for text in [f"Container: {item['container']}", f"Volume: {item['volume_ml']} ml", f"Duration: {item['duration']} s"]:
            self._label(bottom, text, size=25, color="#616161").pack(side="left", padx=20)

    def _run_clock(self):
        self.after(1000, self._run_clock)
