# dashboard.py
# Main dashboard UI showing system status and tank levels

import customtkinter as ctk
from datetime import datetime
import threading
import time
from core.weather_service import get_weather_service

class DashboardPanel(ctk.CTkFrame):
    """Dashboard panel showing system overview"""
    
    def __init__(self, parent, hardware, scheduler):
        super().__init__(parent)
        self.hardware = hardware
        self.scheduler = scheduler
        self.weather_service = get_weather_service()
        
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
        tank_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
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
        container1_frame = ctk.CTkFrame(tanks_container, fg_color="#E8F5E9", corner_radius=10)
        container1_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(
            container1_frame,
            text="CONTAINER 1",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
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
            text_color="#616161"
        )
        self.tank1_liters.pack(pady=(0, 10))
        
        # Container 2
        container2_frame = ctk.CTkFrame(tanks_container, fg_color="#E8F5E9", corner_radius=10)
        container2_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(
            container2_frame,
            text="CONTAINER 2",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
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
            text_color="#616161"
        )
        self.tank2_liters.pack(pady=(0, 10))
        
        # Weather Information Panel
        weather_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
        weather_frame.pack(fill="x", padx=20, pady=10)
        
        weather_title = ctk.CTkLabel(
            weather_frame,
            text="🌤 CURRENT WEATHER",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        weather_title.pack(pady=10)
        
        # Weather content container
        weather_content = ctk.CTkFrame(weather_frame, fg_color="transparent")
        weather_content.pack(fill="x", padx=20, pady=10)
        
        # Left side - Main weather info
        weather_left = ctk.CTkFrame(weather_content, fg_color="#E3F2FD", corner_radius=10)
        weather_left.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        self.weather_condition = ctk.CTkLabel(
            weather_left,
            text="Loading...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1976D2"
        )
        self.weather_condition.pack(pady=(15, 5))
        
        self.weather_temp = ctk.CTkLabel(
            weather_left,
            text="--°C",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#0D47A1"
        )
        self.weather_temp.pack(pady=5)
        
        self.weather_feels_like = ctk.CTkLabel(
            weather_left,
            text="Feels like: --°C",
            font=ctk.CTkFont(size=14),
            text_color="#616161"
        )
        self.weather_feels_like.pack(pady=(0, 15))
        
        # Right side - Additional info
        weather_right = ctk.CTkFrame(weather_content, fg_color="#F3E5F5", corner_radius=10)
        weather_right.pack(side="right", expand=True, fill="both", padx=(10, 0))
        
        self.weather_humidity = ctk.CTkLabel(
            weather_right,
            text="💧 Humidity: --%",
            font=ctk.CTkFont(size=14),
            text_color="#7B1FA2"
        )
        self.weather_humidity.pack(pady=(15, 5))
        
        self.weather_wind = ctk.CTkLabel(
            weather_right,
            text="💨 Wind: -- kph",
            font=ctk.CTkFont(size=14),
            text_color="#7B1FA2"
        )
        self.weather_wind.pack(pady=5)
        
        self.weather_rain = ctk.CTkLabel(
            weather_right,
            text="🌧 Rain: -- mm",
            font=ctk.CTkFont(size=14),
            text_color="#7B1FA2"
        )
        self.weather_rain.pack(pady=5)
        
        self.weather_uv = ctk.CTkLabel(
            weather_right,
            text="☀ UV Index: --",
            font=ctk.CTkFont(size=14),
            text_color="#7B1FA2"
        )
        self.weather_uv.pack(pady=(5, 15))
        
        # Weather update timestamp
        self.weather_updated = ctk.CTkLabel(
            weather_frame,
            text="Updated: Never",
            font=ctk.CTkFont(size=12),
            text_color="#9E9E9E"
        )
        self.weather_updated.pack(pady=(0, 10))
        
        # 
        # System Status
        status_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
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
        next_schedule_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
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
            fg_color="#F5F5F5",
            text_color="#212121",
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
            text_color="#616161"
        )
        self.datetime_label.pack(pady=10)
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                # Schedule UI updates on main thread
                try:
                    self.after(0, self._update_tank_levels)
                    self.after(0, self._update_next_schedule)
                    self.after(0, self._update_datetime)
                    self.after(0, self._update_weather)  # Update weather display
                except:
                    pass  # Widget might be destroyed
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Dashboard update error: {e}")
    
    def _update_tank_levels(self):
        """Update tank level displays using ESP32"""
        if self.hardware:
            try:
                # Use efficient bulk read if connected
                if hasattr(self.hardware, 'get_both_tank_levels') and self.hardware.connected:
                    levels = self.hardware.get_both_tank_levels()
                    level1 = levels.get('tank1', 0.0)
                    level2 = levels.get('tank2', 0.0)
                else:
                    # Fallback to individual reads
                    level1 = self.hardware.get_tank_level_percentage(1)
                    level2 = self.hardware.get_tank_level_percentage(2)
                
                # Update Container 1
                self.tank1_progress.set(level1 / 100)
                self.tank1_label.configure(text=f"{level1:.1f}%")
                # Calculate actual liters based on 16L capacity
                liters1 = (level1 / 100) * 16.0
                self.tank1_liters.configure(text=f"{liters1:.1f} Liters")
                
                # Set color based on level
                if level1 > 50:
                    color1 = "#4CAF50"  # Green
                elif level1 > 20:
                    color1 = "#FF9800"  # Orange
                else:
                    color1 = "#F44336"  # Red
                
                self.tank1_progress.configure(progress_color=color1)
                self.tank1_label.configure(text_color=color1)
                
                # Update Container 2
                self.tank2_progress.set(level2 / 100)
                self.tank2_label.configure(text=f"{level2:.1f}%")
                # Calculate actual liters based on 16L capacity
                liters2 = (level2 / 100) * 16.0
                self.tank2_liters.configure(text=f"{liters2:.1f} Liters")
                
                if level2 > 50:
                    color2 = "#4CAF50"
                elif level2 > 20:
                    color2 = "#FF9800"
                else:
                    color2 = "#F44336"
                
                self.tank2_progress.configure(progress_color=color2)
                self.tank2_label.configure(text_color=color2)
            except Exception as e:
                print(f"Error updating tank levels: {e}")
    
    def _update_next_schedule(self):
        """Update next schedule information"""
        next_schedule = self.scheduler.get_next_schedule()
        
        if next_schedule:
            # Get volume and calculate duration
            volume_ml = next_schedule.get('volume_ml', 1000)
            duration = self.scheduler.calculate_spray_duration(volume_ml)
            
            info_text = (
                f"Date: {next_schedule['date']}\n"
                f"Time: {next_schedule['time']}\n"
                f"Type: {next_schedule['spray_type']}\n"
                f"Container: {next_schedule['container']}\n"
                f"Volume: {volume_ml} mL\n"
                f"Duration: {duration:.1f} seconds\n"
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
    
    def _update_weather(self):
        """Update weather display with hourly cached data"""
        if not self.weather_service or not self.weather_service.available:
            # Weather not available
            self.weather_condition.configure(text="Weather service unavailable")
            self.weather_temp.configure(text="--°C")
            self.weather_feels_like.configure(text="Feels like: --°C")
            self.weather_humidity.configure(text="💧 Humidity: --%")
            self.weather_wind.configure(text="💨 Wind: -- kph")
            self.weather_rain.configure(text="🌧 Rain: -- mm")
            self.weather_uv.configure(text="☀ UV Index: --")
            self.weather_updated.configure(text="Weather API not configured")
            return
        
        try:
            # Get cached weather data (updates hourly automatically)
            weather = self.weather_service.get_current_weather_cached()
            
            if weather:
                # Update main weather info
                condition = weather.get('condition', 'Unknown')
                temp_c = weather.get('temperature_c', 0)
                feels_like = weather.get('feels_like_c', 0)
                humidity = weather.get('humidity', 0)
                wind = weather.get('wind_kph', 0)
                rain = weather.get('precip_mm', 0)
                uv = weather.get('uv', 0)
                
                self.weather_condition.configure(text=condition)
                self.weather_temp.configure(text=f"{temp_c:.1f}°C")
                self.weather_feels_like.configure(text=f"Feels like: {feels_like:.1f}°C")
                
                # Update additional info
                self.weather_humidity.configure(text=f"💧 Humidity: {humidity}%")
                self.weather_wind.configure(text=f"💨 Wind: {wind:.1f} kph")
                
                # Color code rain indicator
                if rain > 0:
                    self.weather_rain.configure(
                        text=f"🌧 Rain: {rain:.1f} mm",
                        text_color="#F44336"  # Red if raining
                    )
                else:
                    self.weather_rain.configure(
                        text=f"🌧 Rain: {rain:.1f} mm",
                        text_color="#7B1FA2"  # Normal color
                    )
                
                # Color code UV index
                if uv >= 8:
                    uv_color = "#D32F2F"  # Very high - red
                elif uv >= 6:
                    uv_color = "#FF6F00"  # High - orange
                elif uv >= 3:
                    uv_color = "#FBC02D"  # Moderate - yellow
                else:
                    uv_color = "#388E3C"  # Low - green
                
                self.weather_uv.configure(
                    text=f"☀ UV Index: {uv:.0f}",
                    text_color=uv_color
                )
                
                # Update timestamp
                cache_age = self.weather_service.get_cache_age()
                if cache_age:
                    self.weather_updated.configure(text=f"Updated: {cache_age}")
                else:
                    self.weather_updated.configure(text="Updated: Never")
            else:
                # Failed to get weather data
                self.weather_condition.configure(text="Unable to fetch weather")
                self.weather_temp.configure(text="--°C")
                self.weather_updated.configure(text="Update failed")
                
        except Exception as e:
            print(f"Error updating weather display: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
