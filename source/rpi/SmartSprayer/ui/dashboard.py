# dashboard.py
# Main dashboard UI showing system status and tank levels

import customtkinter as ctk
from datetime import datetime
import threading
import time

class DashboardPanel(ctk.CTkFrame):
    """Dashboard panel showing system overview"""
    
    def __init__(self, parent, hardware, scheduler):
        super().__init__(parent)
        self.hardware = hardware
        self.scheduler = scheduler
        
        self.configure(fg_color="transparent")
        
        # Create dashboard layout
        self._create_widgets()
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _create_widgets(self):
        """Create dashboard widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="DASHBOARD",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(10, 20))
        
        # Top container - Tank Levels
        tank_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        tank_frame.pack(fill="x", padx=20, pady=10)
        
        tank_title = ctk.CTkLabel(
            tank_frame,
            text="TANK LEVELS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        tank_title.pack(pady=10)
        
        # Tank indicators container
        tanks_container = ctk.CTkFrame(tank_frame, fg_color="transparent")
        tanks_container.pack(fill="x", padx=20, pady=10)
        
        # Container 1
        container1_frame = ctk.CTkFrame(tanks_container, fg_color="#2B2B2B", corner_radius=10)
        container1_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(
            container1_frame,
            text="CONTAINER 1",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=10)
        
        self.tank1_progress = ctk.CTkProgressBar(
            container1_frame,
            width=250,
            height=30,
            corner_radius=10,
            progress_color="#4CAF50"
        )
        self.tank1_progress.pack(pady=10)
        self.tank1_progress.set(0.8)
        
        self.tank1_label = ctk.CTkLabel(
            container1_frame,
            text="80%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.tank1_label.pack(pady=5)
        
        self.tank1_liters = ctk.CTkLabel(
            container1_frame,
            text="80 Liters",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        )
        self.tank1_liters.pack(pady=(0, 10))
        
        # Container 2
        container2_frame = ctk.CTkFrame(tanks_container, fg_color="#2B2B2B", corner_radius=10)
        container2_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(
            container2_frame,
            text="CONTAINER 2",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=10)
        
        self.tank2_progress = ctk.CTkProgressBar(
            container2_frame,
            width=250,
            height=30,
            corner_radius=10,
            progress_color="#4CAF50"
        )
        self.tank2_progress.pack(pady=10)
        self.tank2_progress.set(0.5)
        
        self.tank2_label = ctk.CTkLabel(
            container2_frame,
            text="50%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF9800"
        )
        self.tank2_label.pack(pady=5)
        
        self.tank2_liters = ctk.CTkLabel(
            container2_frame,
            text="50 Liters",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        )
        self.tank2_liters.pack(pady=(0, 10))
        
        # System Status
        status_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="SYSTEM STATUS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        status_title.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="● IDLE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4CAF50"
        )
        self.status_label.pack(pady=20)
        
        # Next Schedule Info
        next_schedule_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        next_schedule_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        next_title = ctk.CTkLabel(
            next_schedule_frame,
            text="NEXT SCHEDULED SPRAY",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        next_title.pack(pady=10)
        
        self.next_schedule_info = ctk.CTkTextbox(
            next_schedule_frame,
            font=ctk.CTkFont(size=16),
            fg_color="#2B2B2B",
            height=150
        )
        self.next_schedule_info.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Time counter
        self.countdown_label = ctk.CTkLabel(
            next_schedule_frame,
            text="Time until spray: --",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2196F3"
        )
        self.countdown_label.pack(pady=(0, 20))
        
        # Current Date/Time
        self.datetime_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA"
        )
        self.datetime_label.pack(pady=10)
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self._update_tank_levels()
                self._update_next_schedule()
                self._update_datetime()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Dashboard update error: {e}")
    
    def _update_tank_levels(self):
        """Update tank level displays"""
        if self.hardware:
            # Container 1
            level1 = self.hardware.get_tank_level_percentage(1)
            self.tank1_progress.set(level1 / 100)
            self.tank1_label.configure(text=f"{level1:.1f}%")
            self.tank1_liters.configure(text=f"{level1:.0f} Liters")
            
            # Set color based on level
            if level1 > 50:
                color1 = "#4CAF50"  # Green
            elif level1 > 20:
                color1 = "#FF9800"  # Orange
            else:
                color1 = "#F44336"  # Red
            
            self.tank1_progress.configure(progress_color=color1)
            self.tank1_label.configure(text_color=color1)
            
            # Container 2
            level2 = self.hardware.get_tank_level_percentage(2)
            self.tank2_progress.set(level2 / 100)
            self.tank2_label.configure(text=f"{level2:.1f}%")
            self.tank2_liters.configure(text=f"{level2:.0f} Liters")
            
            if level2 > 50:
                color2 = "#4CAF50"
            elif level2 > 20:
                color2 = "#FF9800"
            else:
                color2 = "#F44336"
            
            self.tank2_progress.configure(progress_color=color2)
            self.tank2_label.configure(text_color=color2)
    
    def _update_next_schedule(self):
        """Update next schedule information"""
        next_schedule = self.scheduler.get_next_schedule()
        
        if next_schedule:
            info_text = (
                f"Date: {next_schedule['date']}\n"
                f"Time: {next_schedule['time']}\n"
                f"Type: {next_schedule['spray_type']}\n"
                f"Container: {next_schedule['container']}\n"
                f"Status: {next_schedule['status'].upper()}"
            )
            
            self.next_schedule_info.delete("1.0", "end")
            self.next_schedule_info.insert("1.0", info_text)
            
            # Update countdown
            countdown = self.scheduler.get_time_until_next_spray()
            if countdown:
                self.countdown_label.configure(text=f"Time until spray: {countdown}")
            
            # Update status
            self.status_label.configure(
                text=f"● {next_schedule['status'].upper()}",
                text_color="#2196F3"
            )
        else:
            self.next_schedule_info.delete("1.0", "end")
            self.next_schedule_info.insert("1.0", "No upcoming schedules")
            self.countdown_label.configure(text="Time until spray: --")
            self.status_label.configure(text="● IDLE", text_color="#4CAF50")
    
    def _update_datetime(self):
        """Update date/time display"""
        now = datetime.now()
        dt_str = now.strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.datetime_label.configure(text=dt_str)
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
