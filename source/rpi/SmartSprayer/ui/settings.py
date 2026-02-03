import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_store import get_recipients, add_recipient, delete_recipient, update_recipient
from hardware.hardware_interface import get_hardware

class SettingsFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        
        # Get hardware instance
        self.hardware = get_hardware()
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Settings", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # GSM Recipients Section
        self._create_recipients_section()
        
    def _create_recipients_section(self):
        """Create GSM recipients management section"""
        section_frame = ctk.CTkFrame(self)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Section Title
        section_title = ctk.CTkLabel(
            section_frame,
            text="GSM SMS Recipients",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_title.pack(pady=(10, 5))
        
        # Description
        desc = ctk.CTkLabel(
            section_frame,
            text="Manage phone numbers that receive SMS notifications",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc.pack(pady=(0, 10))
        
        # Add recipient section
        add_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=10, pady=10)
        
        add_label = ctk.CTkLabel(
            add_frame,
            text="Add New Recipient:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_label.pack(anchor="w", pady=(0, 5))
        
        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        # Phone number input
        self.phone_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., +639123456789",
            width=200
        )
        self.phone_entry.pack(side="left", padx=(0, 10))
        
        # Name input (optional)
        self.name_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Name (optional)",
            width=150
        )
        self.name_entry.pack(side="left", padx=(0, 10))
        
        # Add button
        self.add_btn = ctk.CTkButton(
            input_frame,
            text="Add Recipient",
            command=self._add_recipient,
            width=120
        )
        self.add_btn.pack(side="left")
        
        # Recipients list
        list_frame = ctk.CTkFrame(section_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="Current Recipients:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Scrollable recipients container
        self.recipients_container = ctk.CTkScrollableFrame(
            list_frame,
            height=300
        )
        self.recipients_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Sync button
        sync_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        sync_frame.pack(fill="x", padx=10, pady=10)
        
        self.sync_btn = ctk.CTkButton(
            sync_frame,
            text="Sync to ESP32",
            command=self._sync_to_esp32,
            width=150
        )
        self.sync_btn.pack()
        
        # Load recipients
        self._refresh_recipients_list()
        
    def _add_recipient(self):
        """Add a new recipient"""
        phone = self.phone_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not phone:
            messagebox.showerror("Error", "Phone number is required")
            return
            
        # Validate phone number format (basic)
        if not phone.startswith("+"):
            messagebox.showerror("Error", "Phone number must start with + (e.g., +639123456789)")
            return
            
        if len(phone) < 10:
            messagebox.showerror("Error", "Invalid phone number format")
            return
        
        # Add to data store
        try:
            success = add_recipient(phone, name if name else phone)
            if success:
                messagebox.showinfo("Success", f"Recipient {name if name else phone} added")
                self.phone_entry.delete(0, 'end')
                self.name_entry.delete(0, 'end')
                self._refresh_recipients_list()
                
                # Send to ESP32
                if self.hardware:
                    self.hardware._send_command(f"add-recipient_{phone}")
            else:
                messagebox.showerror("Error", "Failed to add recipient")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding recipient: {str(e)}")
    
    def _delete_recipient(self, phone):
        """Delete a recipient"""
        if messagebox.askyesno("Confirm Delete", f"Delete recipient {phone}?"):
            try:
                success = delete_recipient(phone)
                if success:
                    messagebox.showinfo("Success", "Recipient deleted")
                    self._refresh_recipients_list()
                    
                    # Remove from ESP32
                    if self.hardware:
                        self.hardware._send_command(f"remove-recipient_{phone}")
                else:
                    messagebox.showerror("Error", "Failed to delete recipient")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting recipient: {str(e)}")
    
    def _sync_to_esp32(self):
        """Sync all recipients to ESP32 using bulk sync"""
        try:
            if not self.hardware:
                messagebox.showerror("Error", "Hardware not available")
                return
            
            if not self.hardware.connected:
                messagebox.showerror("Error", "ESP32 not connected")
                return
            
            recipients = get_recipients()
            
            # Extract phone numbers only for bulk sync
            phone_numbers = [r.get('phone', '') for r in recipients if r.get('phone')]
            
            # Use bulk sync (more efficient)
            success = self.hardware.sync_recipients_bulk(phone_numbers)
            
            if success:
                messagebox.showinfo("Success", f"Synced {len(phone_numbers)} recipients to ESP32")
            else:
                messagebox.showerror("Error", "Failed to sync recipients")
        except Exception as e:
            messagebox.showerror("Error", f"Error syncing to ESP32: {str(e)}")
    
    def _refresh_recipients_list(self):
        """Refresh the recipients list display"""
        # Clear current list
        for widget in self.recipients_container.winfo_children():
            widget.destroy()
        
        # Get recipients
        recipients = get_recipients()
        
        if not recipients:
            no_data = ctk.CTkLabel(
                self.recipients_container,
                text="No recipients added yet",
                text_color="gray"
            )
            no_data.pack(pady=20)
            return
        
        # Display each recipient
        for recipient in recipients:
            self._create_recipient_row(recipient)
    
    def _create_recipient_row(self, recipient):
        """Create a row for a recipient"""
        row_frame = ctk.CTkFrame(self.recipients_container)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        # Info frame
        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=recipient['name'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w")
        
        # Phone
        phone_label = ctk.CTkLabel(
            info_frame,
            text=recipient['phone'],
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        phone_label.pack(anchor="w")
        
        # Delete button
        delete_btn = ctk.CTkButton(
            row_frame,
            text="Delete",
            command=lambda p=recipient['phone']: self._delete_recipient(p),
            fg_color="red",
            hover_color="darkred",
            width=80
        )
        delete_btn.pack(side="right", padx=10, pady=10)
