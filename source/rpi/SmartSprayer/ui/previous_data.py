# previous_data.py
# Previous spray data viewer panel

import customtkinter as ctk
from datetime import datetime

class PreviousDataPanel(ctk.CTkFrame):
    """Previous data panel showing spray history"""
    
    def __init__(self, parent, data_store):
        super().__init__(parent)
        self.data_store = data_store
        
        self.configure(fg_color="transparent")
        
        self._create_widgets()
        self.refresh_data()
    
    def _create_widgets(self):
        """Create data viewer widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="PREVIOUS SPRAY DATA",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(10, 20))
        
        # Controls frame
        controls_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        controls_inner = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_inner.pack(fill="x", padx=15, pady=15)
        
        # Filter options
        filter_label = ctk.CTkLabel(
            controls_inner,
            text="Filter by:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        filter_label.pack(side="left", padx=10)
        
        self.filter_var = ctk.StringVar(value="All")
        
        filter_all = ctk.CTkRadioButton(
            controls_inner,
            text="All",
            variable=self.filter_var,
            value="All",
            font=ctk.CTkFont(size=14),
            command=self.refresh_data
        )
        filter_all.pack(side="left", padx=10)
        
        filter_fert = ctk.CTkRadioButton(
            controls_inner,
            text="Fertilizer",
            variable=self.filter_var,
            value="Fertilizer",
            font=ctk.CTkFont(size=14),
            command=self.refresh_data
        )
        filter_fert.pack(side="left", padx=10)
        
        filter_pest = ctk.CTkRadioButton(
            controls_inner,
            text="Pesticide",
            variable=self.filter_var,
            value="Pesticide",
            font=ctk.CTkFont(size=14),
            command=self.refresh_data
        )
        filter_pest.pack(side="left", padx=10)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(controls_inner, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            font=ctk.CTkFont(size=14),
            height=35,
            width=120,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Export",
            command=self._export_data,
            font=ctk.CTkFont(size=14),
            height=35,
            width=120,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        export_btn.pack(side="left", padx=5)
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="STATISTICS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Total sprays
        total_frame = ctk.CTkFrame(stats_grid, fg_color="#2B2B2B", corner_radius=10)
        total_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(
            total_frame,
            text="Total Sprays",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        ).pack(pady=(10, 5))
        
        self.total_count_label = ctk.CTkLabel(
            total_frame,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_count_label.pack(pady=(5, 10))
        
        # Fertilizer count
        fert_frame = ctk.CTkFrame(stats_grid, fg_color="#2B2B2B", corner_radius=10)
        fert_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(
            fert_frame,
            text="Fertilizer",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        ).pack(pady=(10, 5))
        
        self.fert_count_label = ctk.CTkLabel(
            fert_frame,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2196F3"
        )
        self.fert_count_label.pack(pady=(5, 10))
        
        # Pesticide count
        pest_frame = ctk.CTkFrame(stats_grid, fg_color="#2B2B2B", corner_radius=10)
        pest_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(
            pest_frame,
            text="Pesticide",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        ).pack(pady=(10, 5))
        
        self.pest_count_label = ctk.CTkLabel(
            pest_frame,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FF9800"
        )
        self.pest_count_label.pack(pady=(5, 10))
        
        # Data list
        data_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        data_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            data_frame,
            text="SPRAY HISTORY",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        self.data_list = ctk.CTkScrollableFrame(
            data_frame,
            fg_color="#2B2B2B"
        )
        self.data_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def refresh_data(self):
        """Refresh data display"""
        # Clear existing
        for widget in self.data_list.winfo_children():
            widget.destroy()
        
        # Get history
        history = self.data_store.get_history()
        
        # Apply filter
        filter_type = self.filter_var.get()
        if filter_type != "All":
            history = [h for h in history if h['spray_type'] == filter_type]
        
        # Update statistics
        all_history = self.data_store.get_history()
        total = len(all_history)
        fert_count = len([h for h in all_history if h['spray_type'] == 'Fertilizer'])
        pest_count = len([h for h in all_history if h['spray_type'] == 'Pesticide'])
        
        self.total_count_label.configure(text=str(total))
        self.fert_count_label.configure(text=str(fert_count))
        self.pest_count_label.configure(text=str(pest_count))
        
        # Display history
        if not history:
            no_data_label = ctk.CTkLabel(
                self.data_list,
                text="No spray history available",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            )
            no_data_label.pack(pady=20)
            return
        
        # Reverse to show most recent first
        history.reverse()
        
        for item in history:
            self._create_history_card(item)
    
    def _create_history_card(self, item):
        """Create a card for history item"""
        card = ctk.CTkFrame(self.data_list, fg_color="#1E1E1E", corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        # Date/Time
        date_time = f"{item['date']} at {item['time']}"
        date_label = ctk.CTkLabel(
            header,
            text=date_time,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        date_label.pack(side="left")
        
        # Spray type badge
        spray_type = item['spray_type']
        badge_color = "#2196F3" if spray_type == "Fertilizer" else "#FF9800"
        
        badge = ctk.CTkLabel(
            header,
            text=spray_type,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFFFFF",
            fg_color=badge_color,
            corner_radius=5,
            padx=10,
            pady=5
        )
        badge.pack(side="right")
        
        # Details
        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=15, pady=(0, 10))
        
        # Container info
        container_text = f"Container: {item['container']}"
        ctk.CTkLabel(
            details,
            text=container_text,
            font=ctk.CTkFont(size=13),
            text_color="#CCCCCC"
        ).pack(side="left", padx=5)
        
        # Duration
        duration = item.get('duration', 'N/A')
        duration_text = f"Duration: {duration}s"
        ctk.CTkLabel(
            details,
            text=duration_text,
            font=ctk.CTkFont(size=13),
            text_color="#CCCCCC"
        ).pack(side="left", padx=5)
        
        # Completed time
        completed = item.get('completed_at', 'Unknown')
        try:
            dt = datetime.fromisoformat(completed)
            completed_str = dt.strftime('%I:%M:%S %p')
        except:
            completed_str = completed
        
        completed_text = f"Completed: {completed_str}"
        ctk.CTkLabel(
            details,
            text=completed_text,
            font=ctk.CTkFont(size=13),
            text_color="#AAAAAA"
        ).pack(side="right", padx=5)
    
    def _export_data(self):
        """Export data to JSON file"""
        try:
            from tkinter import filedialog
            import json
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"spray_history_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            if file_path:
                # Export data
                self.data_store.export_data(file_path)
                
                from tkinter import messagebox
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
        
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Export failed: {e}")
