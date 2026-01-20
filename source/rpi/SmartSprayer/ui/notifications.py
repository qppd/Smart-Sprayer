# notifications.py
# Notifications and status display panel

import customtkinter as ctk
from datetime import datetime
import threading
import time

class NotificationsPanel(ctk.CTkFrame):
    """Notifications and status panel"""
    
    def __init__(self, parent, scheduler, data_store, hardware):
        super().__init__(parent)
        self.scheduler = scheduler
        self.data_store = data_store
        self.hardware = hardware
        
        self.configure(fg_color="transparent")
        
        self._create_widgets()
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _create_widgets(self):
        """Create notification widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="NOTIFICATIONS & STATUS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(10, 20))
        
        # System Status Section
        status_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="SYSTEM STATUS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        self.system_status_label = ctk.CTkLabel(
            status_frame,
            text="● IDLE",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.system_status_label.pack(pady=15)
        
        # Tank Status Section
        tank_status_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        tank_status_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            tank_status_frame,
            text="TANK STATUS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        tanks_grid = ctk.CTkFrame(tank_status_frame, fg_color="transparent")
        tanks_grid.pack(fill="x", padx=20, pady=10)
        
        # Container 1 status
        tank1_frame = ctk.CTkFrame(tanks_grid, fg_color="#2B2B2B", corner_radius=10)
        tank1_frame.pack(side="left", expand=True, fill="both", padx=10, pady=5)
        
        ctk.CTkLabel(
            tank1_frame,
            text="CONTAINER 1",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.tank1_status = ctk.CTkLabel(
            tank1_frame,
            text="80% Full",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        self.tank1_status.pack(pady=10)
        
        self.tank1_indicator = ctk.CTkLabel(
            tank1_frame,
            text="✓ OK",
            font=ctk.CTkFont(size=16),
            text_color="#4CAF50"
        )
        self.tank1_indicator.pack(pady=(0, 10))
        
        # Container 2 status
        tank2_frame = ctk.CTkFrame(tanks_grid, fg_color="#2B2B2B", corner_radius=10)
        tank2_frame.pack(side="right", expand=True, fill="both", padx=10, pady=5)
        
        ctk.CTkLabel(
            tank2_frame,
            text="CONTAINER 2",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.tank2_status = ctk.CTkLabel(
            tank2_frame,
            text="50% Full",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FF9800"
        )
        self.tank2_status.pack(pady=10)
        
        self.tank2_indicator = ctk.CTkLabel(
            tank2_frame,
            text="⚠ Low",
            font=ctk.CTkFont(size=16),
            text_color="#FF9800"
        )
        self.tank2_indicator.pack(pady=(0, 10))
        
        # Upcoming Schedule Section
        upcoming_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        upcoming_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            upcoming_frame,
            text="UPCOMING SCHEDULES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        self.upcoming_list = ctk.CTkScrollableFrame(
            upcoming_frame,
            fg_color="#2B2B2B",
            height=200
        )
        self.upcoming_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Recent Activity
        activity_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            activity_frame,
            text="RECENT ACTIVITY",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        self.activity_list = ctk.CTkScrollableFrame(
            activity_frame,
            fg_color="#2B2B2B",
            height=150
        )
        self.activity_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self._update_system_status()
                self._update_tank_status()
                self._update_upcoming_schedules()
                self._update_recent_activity()
                time.sleep(3)
            except Exception as e:
                print(f"Notifications update error: {e}")
    
    def _update_system_status(self):
        """Update system status display"""
        next_schedule = self.scheduler.get_next_schedule()
        
        if next_schedule:
            status = next_schedule.get('status', 'scheduled').upper()
            
            if status == 'EXECUTING':
                self.system_status_label.configure(
                    text="● SPRAYING IN PROGRESS",
                    text_color="#FF9800"
                )
            elif status == 'RESCHEDULED':
                self.system_status_label.configure(
                    text="● RESCHEDULED",
                    text_color="#2196F3"
                )
            else:
                self.system_status_label.configure(
                    text="● SCHEDULED",
                    text_color="#4CAF50"
                )
        else:
            self.system_status_label.configure(
                text="● IDLE",
                text_color="#4CAF50"
            )
    
    def _update_tank_status(self):
        """Update tank status displays"""
        if self.hardware:
            # Container 1
            level1 = self.hardware.get_tank_level_percentage(1)
            self.tank1_status.configure(text=f"{level1:.0f}% Full")
            
            if level1 > 50:
                self.tank1_status.configure(text_color="#4CAF50")
                self.tank1_indicator.configure(text="✓ OK", text_color="#4CAF50")
            elif level1 > 20:
                self.tank1_status.configure(text_color="#FF9800")
                self.tank1_indicator.configure(text="⚠ Low", text_color="#FF9800")
            else:
                self.tank1_status.configure(text_color="#F44336")
                self.tank1_indicator.configure(text="✕ Critical", text_color="#F44336")
            
            # Container 2
            level2 = self.hardware.get_tank_level_percentage(2)
            self.tank2_status.configure(text=f"{level2:.0f}% Full")
            
            if level2 > 50:
                self.tank2_status.configure(text_color="#4CAF50")
                self.tank2_indicator.configure(text="✓ OK", text_color="#4CAF50")
            elif level2 > 20:
                self.tank2_status.configure(text_color="#FF9800")
                self.tank2_indicator.configure(text="⚠ Low", text_color="#FF9800")
            else:
                self.tank2_status.configure(text_color="#F44336")
                self.tank2_indicator.configure(text="✕ Critical", text_color="#F44336")
    
    def _update_upcoming_schedules(self):
        """Update upcoming schedules list"""
        # Clear existing
        for widget in self.upcoming_list.winfo_children():
            widget.destroy()
        
        # Get upcoming schedules (next 5)
        active_schedules = self.data_store.get_active_schedules()
        active_schedules.sort(key=lambda x: f"{x['date']} {x['time']}")
        
        now = datetime.now()
        upcoming = [
            s for s in active_schedules
            if datetime.strptime(f"{s['date']} {s['time']}", '%Y-%m-%d %H:%M') > now
        ][:5]
        
        if not upcoming:
            ctk.CTkLabel(
                self.upcoming_list,
                text="No upcoming schedules",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            ).pack(pady=10)
            return
        
        for schedule in upcoming:
            schedule_item = ctk.CTkFrame(
                self.upcoming_list,
                fg_color="#1E1E1E",
                corner_radius=8
            )
            schedule_item.pack(fill="x", padx=5, pady=5)
            
            date_time_text = f"📅 {schedule['date']} at {schedule['time']}"
            ctk.CTkLabel(
                schedule_item,
                text=date_time_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FFFFFF"
            ).pack(anchor="w", padx=10, pady=(8, 2))
            
            detail_text = f"{schedule['spray_type']} - {schedule['container']}"
            ctk.CTkLabel(
                schedule_item,
                text=detail_text,
                font=ctk.CTkFont(size=12),
                text_color="#AAAAAA"
            ).pack(anchor="w", padx=10, pady=(2, 8))
    
    def _update_recent_activity(self):
        """Update recent activity list"""
        # Clear existing
        for widget in self.activity_list.winfo_children():
            widget.destroy()
        
        # Get recent history (last 5)
        history = self.data_store.get_history(limit=5)
        
        if not history:
            ctk.CTkLabel(
                self.activity_list,
                text="No recent activity",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            ).pack(pady=10)
            return
        
        # Reverse to show most recent first
        history.reverse()
        
        for item in history:
            activity_item = ctk.CTkFrame(
                self.activity_list,
                fg_color="#1E1E1E",
                corner_radius=8
            )
            activity_item.pack(fill="x", padx=5, pady=5)
            
            completed_time = item.get('completed_at', 'Unknown')
            try:
                dt = datetime.fromisoformat(completed_time)
                time_str = dt.strftime('%b %d, %I:%M %p')
            except:
                time_str = completed_time
            
            ctk.CTkLabel(
                activity_item,
                text=f"✓ Completed: {time_str}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#4CAF50"
            ).pack(anchor="w", padx=10, pady=(8, 2))
            
            detail = f"{item['spray_type']} - {item['container']}"
            ctk.CTkLabel(
                activity_item,
                text=detail,
                font=ctk.CTkFont(size=11),
                text_color="#AAAAAA"
            ).pack(anchor="w", padx=10, pady=(2, 8))
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
