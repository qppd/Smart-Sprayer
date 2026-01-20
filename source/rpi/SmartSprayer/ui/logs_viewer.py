# logs_viewer.py
# System logs viewer panel

import customtkinter as ctk
from tkinter import messagebox
import threading
import time

class LogsViewerPanel(ctk.CTkFrame):
    """Logs viewer panel"""
    
    def __init__(self, parent, logger):
        super().__init__(parent)
        self.logger = logger
        
        self.configure(fg_color="transparent")
        
        self._create_widgets()
        
        # Auto-refresh
        self.running = True
        self.auto_refresh = True
        self.update_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.update_thread.start()
        
        # Initial load
        self.refresh_logs()
    
    def _create_widgets(self):
        """Create logs viewer widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="SYSTEM LOGS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(10, 20))
        
        # Controls
        controls_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        controls_inner = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_inner.pack(fill="x", padx=15, pady=15)
        
        # Auto-refresh toggle
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        auto_refresh_check = ctk.CTkCheckBox(
            controls_inner,
            text="Auto-refresh",
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh,
            font=ctk.CTkFont(size=14),
            checkbox_width=24,
            checkbox_height=24
        )
        auto_refresh_check.pack(side="left", padx=10)
        
        # Filter
        filter_label = ctk.CTkLabel(
            controls_inner,
            text="Filter:",
            font=ctk.CTkFont(size=14)
        )
        filter_label.pack(side="left", padx=(20, 5))
        
        self.filter_var = ctk.StringVar(value="All")
        filter_combo = ctk.CTkComboBox(
            controls_inner,
            values=["All", "INFO", "WARNING", "ERROR", "DEBUG"],
            variable=self.filter_var,
            font=ctk.CTkFont(size=14),
            width=120,
            command=lambda _: self.refresh_logs()
        )
        filter_combo.pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(controls_inner, fg_color="transparent")
        btn_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self.refresh_logs,
            font=ctk.CTkFont(size=14),
            height=35,
            width=110,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 Clear Logs",
            command=self._clear_logs,
            font=ctk.CTkFont(size=14),
            height=35,
            width=110,
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        clear_btn.pack(side="left", padx=5)
        
        # Log display
        log_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_title = ctk.CTkLabel(
            log_frame,
            text="LOG ENTRIES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        log_title.pack(pady=10)
        
        # Log text area
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0D0D0D",
            text_color="#00FF00",
            wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA"
        )
        self.status_label.pack(pady=5)
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        self.auto_refresh = self.auto_refresh_var.get()
        status = "enabled" if self.auto_refresh else "disabled"
        self.status_label.configure(text=f"Auto-refresh {status}")
    
    def _auto_refresh_loop(self):
        """Auto-refresh loop"""
        while self.running:
            if self.auto_refresh:
                self.refresh_logs()
            time.sleep(5)  # Refresh every 5 seconds
    
    def refresh_logs(self):
        """Refresh log display"""
        try:
            # Read logs
            log_lines = self.logger.read_logs(num_lines=200)
            
            # Apply filter
            filter_level = self.filter_var.get()
            if filter_level != "All":
                log_lines = [line for line in log_lines if filter_level in line]
            
            # Clear textbox
            self.log_textbox.delete("1.0", "end")
            
            if not log_lines:
                self.log_textbox.insert("1.0", "No log entries found.\n")
                self.status_label.configure(text="No logs")
                return
            
            # Insert logs with color coding
            for line in log_lines:
                # Determine color based on log level
                if "ERROR" in line:
                    color = "#FF5555"
                elif "WARNING" in line:
                    color = "#FFB86C"
                elif "INFO" in line:
                    color = "#50FA7B"
                elif "DEBUG" in line:
                    color = "#8BE9FD"
                else:
                    color = "#F8F8F2"
                
                # Insert line
                start_pos = self.log_textbox.index("end-1c")
                self.log_textbox.insert("end", line)
                
                # Apply color tag
                tag_name = f"color_{color}"
                self.log_textbox.tag_add(tag_name, start_pos, "end-1c")
                self.log_textbox.tag_config(tag_name, foreground=color)
            
            # Scroll to bottom
            self.log_textbox.see("end")
            
            # Update status
            self.status_label.configure(text=f"Loaded {len(log_lines)} log entries")
        
        except Exception as e:
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("1.0", f"Error loading logs: {e}\n")
            self.status_label.configure(text="Error")
    
    def _clear_logs(self):
        """Clear log file"""
        if messagebox.askyesno("Confirm", "Clear all log entries?"):
            try:
                self.logger.clear_logs()
                self.refresh_logs()
                messagebox.showinfo("Success", "Logs cleared successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
