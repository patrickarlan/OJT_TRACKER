"""
Modern OJT Tracker Application
A comprehensive time tracking application for On-the-Job Training with data persistence,
proper architecture, and modern Python practices.

Author: Your Name
Date: February 2026
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

import customtkinter as ctk
import awesometkinter as at
from tkinter import messagebox

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TimeTrackingState(Enum):
    """Enum for different time tracking states."""
    CLOCKED_OUT = "CLOCKED_OUT"
    CLOCKED_IN = "CLOCKED_IN"
    ON_BREAK = "ON_BREAK"


@dataclass
class TimeEntry:
    """Data class for time entries."""
    timestamp: str
    action: str
    duration: Optional[float] = None  # Duration in hours


@dataclass
class UIConfig:
    """Configuration for UI elements."""
    window_width: int = 400
    window_height: int = 400
    corner_radius: int = 10
    frame_color: str = "#242424"
    
    # Colors
    clock_in_color: str = "#4CAF50"
    clock_out_color: str = "#f44336"
    break_color: str = "#FF9800"
    reset_color: str = "#9E9E9E"
    add_time_color: str = "#2196F3"


class DataManager:
    """Handles data persistence for the OJT tracker."""
    
    def __init__(self, data_file: str = "ojt_data.json"):
        self.data_file = Path(data_file)
        self.data: Dict[str, Any] = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {
                "total_hours": 0.0,
                "entries": [],
                "current_session_start": None,
                "state": TimeTrackingState.CLOCKED_OUT.value
            }
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {
                "total_hours": 0.0,
                "entries": [],
                "current_session_start": None,
                "state": TimeTrackingState.CLOCKED_OUT.value
            }
    
    def save_data(self) -> bool:
        """Save data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def add_entry(self, entry: TimeEntry) -> None:
        """Add a time entry."""
        self.data["entries"].append(asdict(entry))
        self.save_data()
    
    def get_total_hours(self) -> float:
        """Get total accumulated hours."""
        return self.data.get("total_hours", 0.0)
    
    def update_total_hours(self, hours: float) -> None:
        """Update total hours."""
        self.data["total_hours"] = hours
        self.save_data()
    
    def get_current_state(self) -> TimeTrackingState:
        """Get current tracking state."""
        state_str = self.data.get("state", TimeTrackingState.CLOCKED_OUT.value)
        return TimeTrackingState(state_str)
    
    def set_current_state(self, state: TimeTrackingState) -> None:
        """Set current tracking state."""
        self.data["state"] = state.value
        self.save_data()
    
    def get_session_start(self) -> Optional[datetime]:
        """Get current session start time."""
        start_str = self.data.get("current_session_start")
        if start_str:
            return datetime.fromisoformat(start_str)
        return None
    
    def set_session_start(self, start_time: Optional[datetime]) -> None:
        """Set current session start time."""
        self.data["current_session_start"] = start_time.isoformat() if start_time else None
        self.save_data()


class TimeTracker:
    """Business logic for time tracking."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.observers: List[Callable] = []
    
    def add_observer(self, callback: Callable) -> None:
        """Add observer for state changes."""
        self.observers.append(callback)
    
    def _notify_observers(self) -> None:
        """Notify all observers of state changes."""
        for callback in self.observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")
    
    def clock_in(self) -> bool:
        """Clock in to start tracking time."""
        try:
            current_state = self.data_manager.get_current_state()
            
            if current_state == TimeTrackingState.CLOCKED_IN:
                messagebox.showwarning("Already Clocked In", "You are already clocked in!")
                return False
            
            now = datetime.now()
            self.data_manager.set_session_start(now)
            self.data_manager.set_current_state(TimeTrackingState.CLOCKED_IN)
            
            entry = TimeEntry(
                timestamp=now.isoformat(),
                action="CLOCK_IN"
            )
            self.data_manager.add_entry(entry)
            
            self._notify_observers()
            logger.info("Clocked in successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clocking in: {e}")
            messagebox.showerror("Error", f"Failed to clock in: {e}")
            return False
    
    def clock_out(self) -> bool:
        """Clock out and calculate session duration."""
        try:
            current_state = self.data_manager.get_current_state()
            
            if current_state == TimeTrackingState.CLOCKED_OUT:
                messagebox.showwarning("Not Clocked In", "You are not currently clocked in!")
                return False
            
            session_start = self.data_manager.get_session_start()
            if not session_start:
                messagebox.showerror("Error", "No session start time found!")
                return False
            
            now = datetime.now()
            duration = (now - session_start).total_seconds() / 3600  # Convert to hours
            
            # Update total hours
            current_total = self.data_manager.get_total_hours()
            self.data_manager.update_total_hours(current_total + duration)
            
            # Create entry
            entry = TimeEntry(
                timestamp=now.isoformat(),
                action="CLOCK_OUT",
                duration=duration
            )
            self.data_manager.add_entry(entry)
            
            # Reset state
            self.data_manager.set_current_state(TimeTrackingState.CLOCKED_OUT)
            self.data_manager.set_session_start(None)
            
            self._notify_observers()
            logger.info(f"Clocked out successfully. Session duration: {duration:.2f} hours")
            messagebox.showinfo("Clocked Out", f"Session completed!\nDuration: {duration:.2f} hours")
            return True
            
        except Exception as e:
            logger.error(f"Error clocking out: {e}")
            messagebox.showerror("Error", f"Failed to clock out: {e}")
            return False
    
    def take_break(self) -> bool:
        """Take a break (pause tracking)."""
        try:
            current_state = self.data_manager.get_current_state()
            
            if current_state == TimeTrackingState.ON_BREAK:
                messagebox.showwarning("Already on Break", "You are already on break!")
                return False
            elif current_state == TimeTrackingState.CLOCKED_OUT:
                messagebox.showwarning("Not Clocked In", "You need to clock in first!")
                return False
            
            now = datetime.now()
            self.data_manager.set_current_state(TimeTrackingState.ON_BREAK)
            
            entry = TimeEntry(
                timestamp=now.isoformat(),
                action="BREAK_START"
            )
            self.data_manager.add_entry(entry)
            
            self._notify_observers()
            logger.info("Break started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting break: {e}")
            messagebox.showerror("Error", f"Failed to start break: {e}")
            return False
    
    def end_break(self) -> bool:
        """End break and resume tracking."""
        try:
            current_state = self.data_manager.get_current_state()
            
            if current_state != TimeTrackingState.ON_BREAK:
                messagebox.showwarning("Not on Break", "You are not currently on break!")
                return False
            
            now = datetime.now()
            self.data_manager.set_current_state(TimeTrackingState.CLOCKED_IN)
            
            entry = TimeEntry(
                timestamp=now.isoformat(),
                action="BREAK_END"
            )
            self.data_manager.add_entry(entry)
            
            self._notify_observers()
            logger.info("Break ended")
            return True
            
        except Exception as e:
            logger.error(f"Error ending break: {e}")
            messagebox.showerror("Error", f"Failed to end break: {e}")
            return False
    
    def reset_time(self) -> bool:
        """Reset all tracked time."""
        try:
            result = messagebox.askyesno(
                "Confirm Reset", 
                "Are you sure you want to reset all tracked time? This cannot be undone!"
            )
            
            if not result:
                return False
            
            self.data_manager.data = {
                "total_hours": 0.0,
                "entries": [],
                "current_session_start": None,
                "state": TimeTrackingState.CLOCKED_OUT.value
            }
            self.data_manager.save_data()
            
            self._notify_observers()
            logger.info("Time tracking reset")
            messagebox.showinfo("Reset Complete", "All time tracking data has been reset.")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting time: {e}")
            messagebox.showerror("Error", f"Failed to reset time: {e}")
            return False
    
    def add_manual_time(self, hours: int, minutes: int, seconds: int) -> bool:
        """Add time manually."""
        try:
            if hours < 0 or minutes < 0 or seconds < 0 or minutes >= 60 or seconds >= 60:
                messagebox.showerror("Invalid Input", "Please enter valid time values!")
                return False
            
            total_hours = hours + (minutes / 60) + (seconds / 3600)
            
            if total_hours == 0:
                messagebox.showwarning("No Time", "Please enter a time greater than 0!")
                return False
            
            # Update total hours
            current_total = self.data_manager.get_total_hours()
            self.data_manager.update_total_hours(current_total + total_hours)
            
            # Create entry
            now = datetime.now()
            entry = TimeEntry(
                timestamp=now.isoformat(),
                action="MANUAL_ADD",
                duration=total_hours
            )
            self.data_manager.add_entry(entry)
            
            self._notify_observers()
            logger.info(f"Added manual time: {total_hours:.2f} hours")
            messagebox.showinfo("Time Added", f"Added {total_hours:.2f} hours to your total.")
            return True
            
        except Exception as e:
            logger.error(f"Error adding manual time: {e}")
            messagebox.showerror("Error", f"Failed to add manual time: {e}")
            return False


class ModernOJTTrackerApp:
    """Modern OJT Tracker Application with proper architecture."""
    
    def __init__(self):
        self.config = UIConfig()
        self.data_manager = DataManager()
        self.time_tracker = TimeTracker(self.data_manager)
        
        # Set up observer
        self.time_tracker.add_observer(self._update_display)
        
        # Set up UI
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.app = ctk.CTk()
        self.app.title("Modern OJT Tracker")
        self.app.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._setup_ui()
        self._center_window()
        self._update_display()
        self._start_datetime_update()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main hours display frame
        self.hours_frame = ctk.CTkFrame(
            self.app, 
            width=200, 
            height=100, 
            fg_color=self.config.frame_color, 
            corner_radius=self.config.corner_radius
        )
        self.hours_frame.place(relx=0.1, rely=0.30, anchor="w")
        
        self.hours_label = ctk.CTkLabel(
            self.hours_frame, 
            text="0.00", 
            font=ctk.CTkFont(size=50, weight="bold")
        )
        self.hours_label.pack(pady=10)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            self.hours_frame,
            text="CLOCKED OUT",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="red"
        )
        self.status_label.pack()
        
        # DateTime frame
        self.datetime_frame = ctk.CTkFrame(
            self.app, 
            width=150, 
            height=60, 
            corner_radius=self.config.corner_radius, 
            fg_color=self.config.frame_color
        )
        self.datetime_frame.place(relx=0.14, rely=0.45, anchor="w")
        
        self.datetime_label = ctk.CTkLabel(
            self.datetime_frame, 
            text="Date and Time", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="white"
        )
        self.datetime_label.pack(pady=10)
        
        # Progress bar
        self.radbar = at.RadialProgressbar(
            self.app, 
            fg='green', 
            parent_bg=self.config.frame_color, 
            size=(150, 150)
        )
        self.radbar.place(relx=0.95, rely=0.37, anchor="e")
        
        # Control buttons frame
        self.button_frame = ctk.CTkFrame(
            self.app, 
            width=300, 
            height=100, 
            corner_radius=self.config.corner_radius, 
            fg_color=self.config.frame_color
        )
        self.button_frame.place(relx=0.05, rely=0.8, anchor="w")
        
        # Action buttons
        self.clock_in_btn = ctk.CTkButton(
            self.button_frame, 
            width=80, 
            text="CLOCK IN", 
            command=self._handle_clock_in,
            fg_color=self.config.clock_in_color
        )
        self.clock_in_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.clock_out_btn = ctk.CTkButton(
            self.button_frame, 
            width=80, 
            text="CLOCK OUT", 
            command=self._handle_clock_out,
            fg_color=self.config.clock_out_color
        )
        self.clock_out_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.break_btn = ctk.CTkButton(
            self.button_frame, 
            width=80, 
            text="BREAK", 
            command=self._handle_break,
            fg_color=self.config.break_color
        )
        self.break_btn.grid(row=1, column=0, padx=10, pady=10)
        
        self.reset_btn = ctk.CTkButton(
            self.button_frame, 
            width=80, 
            text="RESET", 
            command=self._handle_reset,
            fg_color=self.config.reset_color
        )
        self.reset_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Manual time entry
        self.manual_frame = ctk.CTkFrame(
            self.app, 
            width=120, 
            height=60, 
            corner_radius=self.config.corner_radius, 
            fg_color=self.config.frame_color
        )
        self.manual_frame.place(relx=0.95, rely=0.87, anchor="e")
        
        # Time entry widgets
        self.hours_entry = ctk.CTkEntry(
            self.manual_frame, 
            width=35, 
            placeholder_text="HH", 
            justify="center"
        )
        self.hours_entry.grid(row=0, column=0, padx=2, pady=5)
        
        self.minutes_entry = ctk.CTkEntry(
            self.manual_frame, 
            width=35, 
            placeholder_text="MM", 
            justify="center"
        )
        self.minutes_entry.grid(row=0, column=1, padx=2, pady=5)
        
        self.seconds_entry = ctk.CTkEntry(
            self.manual_frame, 
            width=35, 
            placeholder_text="SS", 
            justify="center"
        )
        self.seconds_entry.grid(row=0, column=2, padx=2, pady=5)
        
        # Add time button
        self.add_time_frame = ctk.CTkFrame(
            self.app, 
            width=100, 
            height=50, 
            corner_radius=self.config.corner_radius, 
            fg_color=self.config.frame_color
        )
        self.add_time_frame.place(relx=0.92, rely=0.74, anchor="e")
        
        self.add_time_btn = ctk.CTkButton(
            self.add_time_frame, 
            width=80, 
            text="ADD TIME", 
            command=self._handle_add_time,
            fg_color=self.config.add_time_color
        )
        self.add_time_btn.pack(padx=10, pady=10)
    
    def _center_window(self) -> None:
        """Center the application window on screen."""
        self.app.update_idletasks()
        
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        
        x = int((screen_width / 2) - (self.config.window_width / 2))
        y = int((screen_height / 2) - (self.config.window_height / 2))
        
        self.app.geometry(f"{self.config.window_width}x{self.config.window_height}+{x}+{y}")
    
    def _update_datetime(self) -> None:
        """Update the datetime display."""
        try:
            now = datetime.now()
            current_time = now.strftime("%B %d, %Y\n%I:%M:%S %p")
            self.datetime_label.configure(text=current_time)
        except Exception as e:
            logger.error(f"Error updating datetime: {e}")
        
        # Schedule next update
        self.datetime_label.after(1000, self._update_datetime)
    
    def _start_datetime_update(self) -> None:
        """Start the datetime update loop."""
        self._update_datetime()
    
    def _update_display(self) -> None:
        """Update the display with current data."""
        try:
            # Update hours display
            total_hours = self.data_manager.get_total_hours()
            self.hours_label.configure(text=f"{total_hours:.2f}")
            
            # Update progress bar (assuming 300 hours target)
            progress = min(total_hours / 300.0, 1.0) * 100
            self.radbar.set(progress)
            
            # Update status
            current_state = self.data_manager.get_current_state()
            status_colors = {
                TimeTrackingState.CLOCKED_OUT: "red",
                TimeTrackingState.CLOCKED_IN: "green", 
                TimeTrackingState.ON_BREAK: "orange"
            }
            
            self.status_label.configure(
                text=current_state.value.replace("_", " "),
                text_color=status_colors[current_state]
            )
            
            # Update button states
            self._update_button_states(current_state)
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def _update_button_states(self, current_state: TimeTrackingState) -> None:
        """Update button enabled/disabled states based on current state."""
        if current_state == TimeTrackingState.CLOCKED_OUT:
            self.clock_in_btn.configure(state="normal")
            self.clock_out_btn.configure(state="disabled")
            self.break_btn.configure(text="BREAK", state="disabled")
        elif current_state == TimeTrackingState.CLOCKED_IN:
            self.clock_in_btn.configure(state="disabled")
            self.clock_out_btn.configure(state="normal")
            self.break_btn.configure(text="BREAK", state="normal")
        elif current_state == TimeTrackingState.ON_BREAK:
            self.clock_in_btn.configure(state="disabled")
            self.clock_out_btn.configure(state="normal")
            self.break_btn.configure(text="END BREAK", state="normal")
    
    def _handle_clock_in(self) -> None:
        """Handle clock in button press."""
        self.time_tracker.clock_in()
    
    def _handle_clock_out(self) -> None:
        """Handle clock out button press."""
        self.time_tracker.clock_out()
    
    def _handle_break(self) -> None:
        """Handle break button press."""
        current_state = self.data_manager.get_current_state()
        if current_state == TimeTrackingState.ON_BREAK:
            self.time_tracker.end_break()
        else:
            self.time_tracker.take_break()
    
    def _handle_reset(self) -> None:
        """Handle reset button press."""
        self.time_tracker.reset_time()
    
    def _handle_add_time(self) -> None:
        """Handle add time button press."""
        try:
            hours_str = self.hours_entry.get() or "0"
            minutes_str = self.minutes_entry.get() or "0"
            seconds_str = self.seconds_entry.get() or "0"
            
            hours = int(hours_str)
            minutes = int(minutes_str)
            seconds = int(seconds_str)
            
            if self.time_tracker.add_manual_time(hours, minutes, seconds):
                # Clear entries on success
                self.hours_entry.delete(0, 'end')
                self.minutes_entry.delete(0, 'end')
                self.seconds_entry.delete(0, 'end')
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers!")
    
    def _on_closing(self) -> None:
        """Handle application closing."""
        try:
            # Save any pending data
            self.data_manager.save_data()
            logger.info("Application closing - data saved")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self.app.destroy()
    
    def run(self) -> None:
        """Run the application."""
        try:
            logger.info("Starting Modern OJT Tracker application")
            self.app.mainloop()
        except Exception as e:
            logger.error(f"Error running application: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {e}")


def main() -> None:
    """Main entry point."""
    try:
        app = ModernOJTTrackerApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()