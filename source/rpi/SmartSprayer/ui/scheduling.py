# scheduling.py
# Scheduling UI with calendar, time picker, and recurring options

import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import uuid

class SchedulingPanel(ctk.CTkFrame):
    """Scheduling panel for creating and managing spray schedules"""
    
    def __init__(self, parent, scheduler, reschedule_mgr, logger):
        super().__init__(parent)
        self.scheduler = scheduler
        self.reschedule_mgr = reschedule_mgr
        self.logger = logger
        
        self.configure(fg_color="transparent")
        
        # Initialize critical attributes to prevent AttributeError if widget creation fails
        self.date_entry = None  # Keep for backward compatibility
        self.year_cb = None
        self.month_cb = None
        self.day_cb = None
        
        try:
            self._create_widgets()
            self.refresh_schedule_list()
        except Exception as e:
            self.logger.log_error(f"SchedulingPanel initialization error: {e}")
            print(f"[UI] Error initializing SchedulingPanel: {e}")
    
    def _create_widgets(self):
        """Create scheduling widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="SCHEDULING",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(10, 20))
        
        # Main container with two columns
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # LEFT COLUMN - Schedule Form
        form_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        form_title = ctk.CTkLabel(
            form_frame,
            text="CREATE NEW SCHEDULE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        form_title.pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Date Selection
        date_label = ctk.CTkLabel(
            form_scroll,
            text="SELECT DATE:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        date_label.pack(anchor="w", pady=(10, 5))
        
        date_container = ctk.CTkFrame(form_scroll, fg_color="transparent")
        date_container.pack(fill="x", pady=5)
        
        current_year = datetime.now().year
        self.year_cb = ctk.CTkComboBox(
            date_container,
            values=[str(y) for y in range(current_year, current_year + 2)],
            font=ctk.CTkFont(size=14),
            width=80
        )
        self.year_cb.set(str(current_year))
        self.year_cb.pack(side="left", padx=5)
        
        self.month_cb = ctk.CTkComboBox(
            date_container,
            values=[f"{i:02d}" for i in range(1, 13)],
            font=ctk.CTkFont(size=14),
            width=70
        )
        self.month_cb.set(f"{datetime.now().month:02d}")
        self.month_cb.pack(side="left", padx=5)
        
        self.day_cb = ctk.CTkComboBox(
            date_container,
            values=[f"{i:02d}" for i in range(1, 32)],
            font=ctk.CTkFont(size=14),
            width=70
        )
        self.day_cb.set(f"{datetime.now().day:02d}")
        self.day_cb.pack(side="left", padx=5)
        
        # Time Selection
        time_label = ctk.CTkLabel(
            form_scroll,
            text="SELECT TIME:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        time_label.pack(anchor="w", pady=(15, 5))
        
        time_container = ctk.CTkFrame(form_scroll, fg_color="transparent")
        time_container.pack(fill="x", pady=5)
        
        self.hour_spinbox = ctk.CTkComboBox(
            time_container,
            values=[f"{i:02d}" for i in range(24)],
            font=ctk.CTkFont(size=14),
            width=100,
            height=40
        )
        self.hour_spinbox.set("08")
        self.hour_spinbox.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            time_container,
            text=":",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=5)
        
        self.minute_spinbox = ctk.CTkComboBox(
            time_container,
            values=[f"{i:02d}" for i in range(0, 60, 5)],
            font=ctk.CTkFont(size=14),
            width=100,
            height=40
        )
        self.minute_spinbox.set("00")
        self.minute_spinbox.pack(side="left", padx=5)
        
        # Spray Type
        spray_type_label = ctk.CTkLabel(
            form_scroll,
            text="SPRAY TYPE:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        spray_type_label.pack(anchor="w", pady=(15, 5))
        
        self.spray_type_var = ctk.StringVar(value="Fertilizer")
        spray_type_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        spray_type_frame.pack(fill="x", pady=5)
        
        ctk.CTkRadioButton(
            spray_type_frame,
            text="Fertilizer",
            variable=self.spray_type_var,
            value="Fertilizer",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            spray_type_frame,
            text="Pesticide",
            variable=self.spray_type_var,
            value="Pesticide",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        ).pack(side="left", padx=10)
        
        # Container Selection
        container_label = ctk.CTkLabel(
            form_scroll,
            text="CONTAINER:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        container_label.pack(anchor="w", pady=(15, 5))
        
        self.container_var = ctk.StringVar(value="Container 1")
        container_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        container_frame.pack(fill="x", pady=5)
        
        ctk.CTkRadioButton(
            container_frame,
            text="Container 1",
            variable=self.container_var,
            value="Container 1",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            container_frame,
            text="Container 2",
            variable=self.container_var,
            value="Container 2",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        ).pack(side="left", padx=10)
        
        # Volume Input (mL)
        volume_label = ctk.CTkLabel(
            form_scroll,
            text="SPRAY VOLUME (mL):",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        volume_label.pack(anchor="w", pady=(15, 5))
        
        volume_input_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        volume_input_frame.pack(fill="x", pady=5)
        
        self.volume_entry = ctk.CTkEntry(
            volume_input_frame,
            placeholder_text="e.g., 1000",
            font=ctk.CTkFont(size=14),
            height=40,
            width=150
        )
        self.volume_entry.insert(0, "1000")  # Default 1000 mL
        self.volume_entry.pack(side="left", padx=5)
        
        volume_unit_label = ctk.CTkLabel(
            volume_input_frame,
            text="mL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        )
        volume_unit_label.pack(side="left", padx=5)
        
        # Duration calculation info (based on 5L/min pump rate)
        self.duration_info_label = ctk.CTkLabel(
            form_scroll,
            text="Duration: Calculated based on pump rate (5L/min)",
            font=ctk.CTkFont(size=12),
            text_color="#616161"
        )
        self.duration_info_label.pack(anchor="w", pady=(2, 0))
        
        # Recurring Options
        recurring_label = ctk.CTkLabel(
            form_scroll,
            text="RECURRING (Optional):",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        recurring_label.pack(anchor="w", pady=(15, 5))
        
        self.recurring_var = ctk.BooleanVar(value=False)
        recurring_check = ctk.CTkCheckBox(
            form_scroll,
            text="Enable Recurring Schedule",
            variable=self.recurring_var,
            command=self._toggle_recurring,
            font=ctk.CTkFont(size=14),
            checkbox_width=24,
            checkbox_height=24
        )
        recurring_check.pack(anchor="w", pady=5)
        
        self.recurring_frame = ctk.CTkFrame(form_scroll, fg_color="#E8F5E9", corner_radius=10)
        
        interval_label = ctk.CTkLabel(
            self.recurring_frame,
            text="Interval (days):",
            font=ctk.CTkFont(size=14)
        )
        interval_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.interval_entry = ctk.CTkEntry(
            self.recurring_frame,
            placeholder_text="e.g., 7",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.interval_entry.pack(fill="x", padx=10, pady=5)
        
        count_label = ctk.CTkLabel(
            self.recurring_frame,
            text="Number of occurrences:",
            font=ctk.CTkFont(size=14)
        )
        count_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.count_entry = ctk.CTkEntry(
            self.recurring_frame,
            placeholder_text="e.g., 4",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.count_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 10))
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="✓ CREATE SCHEDULE",
            command=self._create_schedule,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        create_btn.pack(fill="x", pady=5)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            command=self._clear_form,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#757575",
            hover_color="#616161"
        )
        clear_btn.pack(fill="x", pady=5)
        
        # RIGHT COLUMN - Schedule List
        list_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15)
        list_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="ACTIVE SCHEDULES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        list_title.pack(pady=15)
        
        # Schedule list
        self.schedule_list = ctk.CTkScrollableFrame(list_frame, fg_color="#F5F5F5")
        self.schedule_list.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Action buttons
        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Refresh",
            command=self.refresh_schedule_list,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_btn.pack(fill="x", pady=5)
        
        clear_all_btn = ctk.CTkButton(
            action_frame,
            text="✕ Cancel All Schedules",
            command=self._cancel_all_schedules,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        clear_all_btn.pack(fill="x", pady=5)
    
    def _toggle_recurring(self):
        """Toggle recurring options visibility"""
        if self.recurring_var.get():
            self.recurring_frame.pack(fill="x", padx=10, pady=10)
        else:
            self.recurring_frame.pack_forget()
    
    def _create_schedule(self):
        """Create new schedule(s)"""
        # Safety check for widget initialization
        if self.year_cb is None or self.month_cb is None or self.day_cb is None:
            messagebox.showerror("Error", "Scheduling panel not properly initialized. Please restart the application.")
            return
        
        # Validate inputs
        year = self.year_cb.get()
        month = self.month_cb.get()
        day = self.day_cb.get()
        date = f"{year}-{month}-{day}"
        
        hour = self.hour_spinbox.get()
        minute = self.minute_spinbox.get()
        time = f"{hour}:{minute}"
        
        spray_type = self.spray_type_var.get()
        container = self.container_var.get()
        
        # Get and validate volume
        try:
            volume_ml = float(self.volume_entry.get())
            if volume_ml <= 0:
                messagebox.showerror("Error", "Volume must be greater than 0 mL")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid volume in mL")
            return
        
        try:
            if self.recurring_var.get():
                # Create recurring schedules
                interval = int(self.interval_entry.get())
                count = int(self.count_entry.get())
                
                if interval < 1 or count < 2:
                    messagebox.showerror("Error", "Invalid interval or count")
                    return
                
                schedules = self.scheduler.create_recurring_schedules(
                    date, interval, count, time, spray_type, container, volume_ml
                )
                
                messagebox.showinfo(
                    "Success",
                    f"Created {len(schedules)} recurring schedules with {interval}-day interval\nVolume: {volume_ml} mL per spray"
                )
            else:
                # Create single schedule
                schedule = self.scheduler.create_schedule(
                    date, time, spray_type, container, volume_ml
                )
                
                # Calculate duration for display
                duration = self.scheduler.calculate_spray_duration(volume_ml)
                
                messagebox.showinfo(
                    "Success",
                    f"Schedule created for {date} at {time}\nVolume: {volume_ml} mL\nDuration: {duration:.1f} seconds"
                )
            
            self._clear_form()
            self.refresh_schedule_list()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create schedule: {e}")
            self.logger.log_error(f"Schedule creation error: {e}")
    
    def _clear_form(self):
        """Clear form fields"""
        self.date_entry.configure(state="normal")
        self.date_entry.delete(0, "end")
        self.date_entry.configure(state="readonly")
        self.hour_spinbox.set("08")
        self.minute_spinbox.set("00")
        self.spray_type_var.set("Fertilizer")
        self.container_var.set("Container 1")
        self.volume_entry.delete(0, "end")
        self.volume_entry.insert(0, "1000")  # Reset to default 1000 mL
        self.recurring_var.set(False)
        self.interval_entry.delete(0, "end")
        self.count_entry.delete(0, "end")
        self._toggle_recurring()
    
    def refresh_schedule_list(self):
        """Refresh the schedule list display"""
        # Clear existing items
        for widget in self.schedule_list.winfo_children():
            widget.destroy()
        
        # Get active schedules
        schedules = self.scheduler.data_store.get_active_schedules()
        
        if not schedules:
            no_schedule_label = ctk.CTkLabel(
                self.schedule_list,
                text="No active schedules",
                font=ctk.CTkFont(size=14),
                text_color="#616161"
            )
            no_schedule_label.pack(pady=20)
            return
        
        # Sort schedules by date and time
        schedules.sort(key=lambda x: f"{x['date']} {x['time']}")
        
        # Display schedules
        for schedule in schedules:
            self._create_schedule_card(schedule)
    
    def _create_schedule_card(self, schedule):
        """Create a card widget for a schedule"""
        card = ctk.CTkFrame(self.schedule_list, fg_color="#FFFFFF", corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)
        
        # Header with date/time
        header = ctk.CTkFrame(card, fg_color="#4CAF50", corner_radius=8)
        header.pack(fill="x", padx=3, pady=3)
        
        header_text = f"{schedule['date']} at {schedule['time']}"
        ctk.CTkLabel(
            header,
            text=header_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=8)
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get volume and calculate duration
        volume_ml = schedule.get('volume_ml', 1000)
        duration = self.scheduler.calculate_spray_duration(volume_ml)
        
        info_text = (
            f"Type: {schedule['spray_type']}\n"
            f"Container: {schedule['container']}\n"
            f"Volume: {volume_ml} mL\n"
            f"Duration: {duration:.1f} seconds\n"
            f"Status: {schedule['status'].upper()}\n"
            f"Reschedules: {schedule.get('reschedule_count', 0)}/{self.reschedule_mgr.MAX_RESCHEDULES}"
        )
        
        ctk.CTkLabel(
            content,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="#424242",
            justify="left"
        ).pack(anchor="w", pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        reschedule_btn = ctk.CTkButton(
            btn_frame,
            text="Reschedule",
            command=lambda s=schedule: self._open_reschedule_dialog(s),
            font=ctk.CTkFont(size=12),
            height=30,
            width=100,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        reschedule_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=lambda s=schedule: self._cancel_schedule(s),
            font=ctk.CTkFont(size=12),
            height=30,
            width=100,
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        cancel_btn.pack(side="left", padx=5)
    
    def _open_reschedule_dialog(self, schedule):
        """Open dialog to reschedule"""
        # Create popup
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Reschedule: {schedule['id']}")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="RESCHEDULE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=15)
        
        # Date
        ctk.CTkLabel(dialog, text="New Date:", font=ctk.CTkFont(size=14)).pack(pady=5)
        
        date_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        date_frame.pack(pady=5)
        
        current_year = datetime.now().year
        new_year = ctk.CTkComboBox(date_frame, values=[str(y) for y in range(current_year, current_year + 2)], width=80)
        new_year.set(schedule['date'].split('-')[0])
        new_year.pack(side="left", padx=5)
        
        new_month = ctk.CTkComboBox(date_frame, values=[f"{i:02d}" for i in range(1, 13)], width=70)
        new_month.set(schedule['date'].split('-')[1])
        new_month.pack(side="left", padx=5)
        
        new_day = ctk.CTkComboBox(date_frame, values=[f"{i:02d}" for i in range(1, 32)], width=70)
        new_day.set(schedule['date'].split('-')[2])
        new_day.pack(side="left", padx=5)
        
        # Time
        ctk.CTkLabel(dialog, text="New Time:", font=ctk.CTkFont(size=14)).pack(pady=5)
        
        time_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        time_frame.pack(pady=5)
        
        new_hour = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(24)], width=80)
        new_hour.set(schedule['time'].split(':')[0])
        new_hour.pack(side="left", padx=5)
        
        ctk.CTkLabel(time_frame, text=":", font=ctk.CTkFont(size=16)).pack(side="left")
        
        new_minute = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], width=80)
        new_minute.set(schedule['time'].split(':')[1])
        new_minute.pack(side="left", padx=5)
        
        def confirm_reschedule():
            new_date = f"{new_year.get()}-{new_month.get()}-{new_day.get()}"
            
            new_time = f"{new_hour.get()}:{new_minute.get()}"
            
            success, message, affected = self.reschedule_mgr.reschedule(
                schedule['id'], new_date, new_time
            )
            
            if success:
                msg = f"Schedule rescheduled to {new_date} at {new_time}"
                if affected:
                    msg += f"\n\n{len(affected)} other schedule(s) auto-adjusted:"
                    for aff in affected[:3]:
                        msg += f"\n- {aff['id']}: {aff['old_date']} → {aff['new_date']}"
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.refresh_schedule_list()
            else:
                messagebox.showerror("Error", message)
                dialog.destroy()
                self.refresh_schedule_list()
        
        ctk.CTkButton(
            dialog,
            text="✓ Confirm Reschedule",
            command=confirm_reschedule,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="#4CAF50"
        ).pack(fill="x", padx=20, pady=20)
    
    def _cancel_schedule(self, schedule):
        """Cancel a single schedule"""
        if messagebox.askyesno("Confirm", f"Cancel schedule on {schedule['date']}?"):
            self.reschedule_mgr.cancel_schedule(schedule['id'])
            messagebox.showinfo("Success", "Schedule cancelled")
            self.refresh_schedule_list()
    
    def _cancel_all_schedules(self):
        """Cancel all active schedules"""
        if messagebox.askyesno("Confirm", "Cancel ALL active schedules?"):
            self.reschedule_mgr.cancel_all_schedules()
            messagebox.showinfo("Success", "All schedules cancelled")
            self.refresh_schedule_list()
