# main_ui.py
# Main application UI - Smart Sprayer GUI

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.hardware_interface import get_hardware
from core.logger import get_logger
from core.data_store import get_data_store
from core.scheduler import get_scheduler
from core.reschedule_logic import get_reschedule_manager

from ui.dashboard import DashboardPanel
from ui.scheduling import SchedulingPanel
from ui.previous_data import PreviousDataPanel
from ui.notifications import NotificationsPanel
from ui.logs_viewer import LogsViewerPanel


class SmartSprayerUI(ctk.CTk):
    """Main Smart Sprayer GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Smart Sprayer Control System")
        self.geometry("1400x900")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Initialize backend components
        self.logger = get_logger()
        self.logger.log_info("=== Smart Sprayer GUI Started ===")
        
        self.hardware = get_hardware()
        self.data_store = get_data_store()
        self.scheduler = get_scheduler(self.hardware)
        self.reschedule_mgr = get_reschedule_manager()
        
        # Start scheduler
        self.scheduler.start()
        
        # Create UI
        self._create_ui()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.log_info("GUI initialization complete")
    
    def _create_ui(self):
        """Create main UI layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # LEFT SIDEBAR - Navigation
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1A1A1A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # Logo/Title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="#4CAF50", height=100)
        logo_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        logo_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            logo_frame,
            text="🌱",
            font=ctk.CTkFont(size=40)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            logo_frame,
            text="SMART SPRAYER",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        ).pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "📊", "dashboard"),
            ("Scheduling", "📅", "scheduling"),
            ("Previous Data", "📋", "previous_data"),
            ("Notifications", "🔔", "notifications"),
            ("System Logs", "📝", "logs")
        ]
        
        for i, (text, icon, key) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {text}",
                font=ctk.CTkFont(size=16),
                height=50,
                corner_radius=10,
                fg_color="transparent",
                text_color="#FFFFFF",
                hover_color="#2B2B2B",
                anchor="w",
                command=lambda k=key: self._show_panel(k)
            )
            btn.grid(row=i+1, column=0, padx=15, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        # System info at bottom
        self.system_info = ctk.CTkLabel(
            self.sidebar,
            text="System: PC Mode\nStatus: Running",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            justify="left"
        )
        self.system_info.grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
        # About button
        about_btn = ctk.CTkButton(
            self.sidebar,
            text="ℹ About",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#757575",
            hover_color="#616161",
            command=self._show_about
        )
        about_btn.grid(row=9, column=0, padx=15, pady=10, sticky="ew")
        
        # RIGHT CONTENT AREA
        self.content_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create panels (hidden initially)
        self.panels = {}
        
        self.panels["dashboard"] = DashboardPanel(
            self.content_frame, 
            self.hardware, 
            self.scheduler
        )
        
        self.panels["scheduling"] = SchedulingPanel(
            self.content_frame,
            self.scheduler,
            self.reschedule_mgr,
            self.logger
        )
        
        self.panels["previous_data"] = PreviousDataPanel(
            self.content_frame,
            self.data_store
        )
        
        self.panels["notifications"] = NotificationsPanel(
            self.content_frame,
            self.scheduler,
            self.data_store,
            self.hardware
        )
        
        self.panels["logs"] = LogsViewerPanel(
            self.content_frame,
            self.logger
        )
        
        # Show dashboard by default
        self._show_panel("dashboard")
    
    def _show_panel(self, panel_key):
        """Show selected panel and hide others"""
        # Hide all panels
        for key, panel in self.panels.items():
            panel.pack_forget()
        
        # Reset all button colors
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent")
        
        # Show selected panel
        if panel_key in self.panels:
            self.panels[panel_key].pack(fill="both", expand=True)
            
            # Highlight selected button
            if panel_key in self.nav_buttons:
                self.nav_buttons[panel_key].configure(fg_color="#4CAF50")
            
            self.logger.log_debug(f"Switched to panel: {panel_key}")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = (
            "Smart Sprayer Control System\n\n"
            "Version: 1.0.0\n"
            "Developed for: Agricultural Automation\n\n"
            "Features:\n"
            "• Automated spray scheduling\n"
            "• Tank level monitoring\n"
            "• Reschedule with auto-adjust\n"
            "• Comprehensive logging\n"
            "• Farmer-friendly UI\n\n"
            "Mode: PC Testing (Mock Hardware)\n"
            "Ready for Raspberry Pi deployment"
        )
        
        messagebox.showinfo("About Smart Sprayer", about_text)
    
    def _on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit Smart Sprayer?"):
            self.logger.log_info("=== Shutting down Smart Sprayer ===")
            
            # Stop scheduler
            self.scheduler.stop()
            
            # Cleanup hardware
            if self.hardware:
                self.hardware.cleanup()
            
            # Cleanup panels
            for panel in self.panels.values():
                if hasattr(panel, 'cleanup'):
                    panel.cleanup()
            
            self.logger.log_info("Shutdown complete")
            self.destroy()


def main():
    """Main entry point"""
    # Create and run application
    app = SmartSprayerUI()
    app.mainloop()


if __name__ == "__main__":
    main()
