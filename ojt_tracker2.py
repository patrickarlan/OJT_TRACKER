from turtle import color

import customtkinter as ctk
import tkinter as tk
import awesometkinter as at
import json
import os
import time
import sys
import atexit

from tkcalendar import Calendar
from tkinter import Toplevel
from cProfile import label
from tkinter import ttk, messagebox
from datetime import datetime, date

# SINGLE INSTANCE CHECK
LOCK_FILE = "ojt_tracker.lock"

def check_single_instance():
    """Check if another instance of the application is already running"""
    if os.path.exists(LOCK_FILE):
        try:
            # Check if the process is still running by trying to read the PID
            with open(LOCK_FILE, 'r') as f:
                old_pid = f.read().strip()
            
            # Try to check if process is still running (Windows/Unix compatible)
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {old_pid}'], 
                                          capture_output=True, text=True)
                    if old_pid in result.stdout:
                        messagebox.showerror(
                            "Already Running", 
                            "OJT Tracker is already running!\nPlease close the existing instance first."
                        )
                        sys.exit(1)
                else:  # Unix/Linux/Mac
                    os.kill(int(old_pid), 0)
                    messagebox.showerror(
                        "Already Running", 
                        "OJT Tracker is already running!\nPlease close the existing instance first."
                    )
                    sys.exit(1)
            except (subprocess.CalledProcessError, ProcessLookupError, ValueError):
                # Process not found, remove stale lock file
                os.remove(LOCK_FILE)
        except Exception:
            # Error reading lock file, assume it's stale and remove it
            try:
                os.remove(LOCK_FILE)
            except:
                pass
    
    # Create lock file with current process ID
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        messagebox.showerror("Error", f"Could not create lock file: {e}")
        sys.exit(1)

def cleanup_lock_file():
    """Remove the lock file when application exits"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass

# Register cleanup function to run on exit
atexit.register(cleanup_lock_file)

# Check for single instance before creating the app
check_single_instance()

calendar_window = None
note_window = None
daily_notes = {}
daily_status = {}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("OJT Tracker")


#CENTERING THE APP ON THE SCREEN
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

window_width = 400
window_height = 400

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

app.geometry(f"{window_width}x{window_height}+{x}+{y}")

# FRAMES
hours_frame = ctk.CTkFrame(app, width=100, height=100, fg_color="#242424", corner_radius=10)
hours_frame.place(relx=0.1, rely=0.30, anchor="w")

status_frame = ctk.CTkFrame(app, width=100, height=30, corner_radius=10, fg_color="#242424")
status_frame.place(relx=0.14, rely=0.55, anchor="w")

# button_frame = ctk.CTkFrame(app, width=300, height=100, corner_radius=10, fg_color="#242424")
# button_frame.place(relx=0.05, rely=0.8, anchor="w")
# button_frame.grid_propagate(True)

button_frame2 = ctk.CTkFrame(app, width=100, height=50, corner_radius=10, fg_color="#242424")
button_frame2.place(relx=0.90, rely=0.74, anchor="e")

manual_time_frame = ctk.CTkFrame(app, width=120, height=30, corner_radius=10, fg_color="#242424")
manual_time_frame.place(relx=0.93, rely=0.86, anchor="e")

datetime_frame = ctk.CTkFrame(app, width=150, height=30, corner_radius=10, fg_color="#242424")
datetime_frame.place(relx=0.14, rely=0.45, anchor="w")

frame3d_in = at.Frame3d(app, bg="#2b2b2b")
frame3d_in.place(relx=0.05, rely=0.8, anchor="w")

# LABELS
hours_label = ctk.CTkLabel(hours_frame, text="300.00", font=ctk.CTkFont(size=50, weight="bold"))
hours_label.pack(pady=1)

status_label = ctk.CTkLabel(status_frame, text="Status: Clocked Out", font=ctk.CTkFont(size=14))
status_label.pack(pady=5)

# Last closed label
last_closed_frame = ctk.CTkFrame(app, width=200, height=30, corner_radius=10, fg_color="#242424")
last_closed_frame.place(relx=0.5, rely=0.62, anchor="center")

last_closed_label = ctk.CTkLabel(
    last_closed_frame, 
    text="Never closed", 
    font=ctk.CTkFont(size=15), 
    text_color="gray"
)
last_closed_label.pack(pady=5)

datetime_label = ctk.CTkLabel(
    datetime_frame, 
    text="Date and Time", 
    font=ctk.CTkFont(size=14, weight="bold"), 
    text_color="white")

# PROGRESS BAR
try:
    radbar2 = at.RadialProgressbar3d(app, fg='green', parent_bg="#242424", size=(150,150))
    radbar2.place(relx=0.95, rely=0.37, anchor="e")
    radbar2.set(100)  
except AttributeError:
    print("RadialProgressbar not found, using alternative")


# FUNCTION FOR THE BUTTONS  
def button_click():
    messagebox.showinfo("Button Clicked", "You clicked the button!")

def clock_in_button():
    clock_in()

def clock_out_button():
    clock_out()
    
def breakOut():
    breakOut()
    
def rest_button_click():
    resethrs()

def add_manual_time():
    """Add manual time from the HH:MM:SS entries"""
    try:
        hours_str = manual_time_entry.get().strip()
        minutes_str = manual_time_entry2.get().strip()
        seconds_str = manual_time_entry3.get().strip()
        
        hours = int(hours_str) if hours_str else 0
        minutes = int(minutes_str) if minutes_str else 0
        seconds = int(seconds_str) if seconds_str else 0
        
        if hours < 0 or minutes < 0 or seconds < 0:
            messagebox.showerror("Invalid Input", "Time values cannot be negative!")
            return
            
        if minutes >= 60:
            messagebox.showerror("Invalid Input", "Minutes must be less than 60!")
            return
            
        if seconds >= 60:
            messagebox.showerror("Invalid Input", "Seconds must be less than 60!")
            return
            
        if hours == 0 and minutes == 0 and seconds == 0:
            messagebox.showwarning("No Time Entered", "Please enter the time you want to add!")
            return
        
        manual_seconds = (hours * 3600) + (minutes * 60) + seconds
        
        time_display = f"{hours}h {minutes}m {seconds}s"
        result = messagebox.askyesno(
            "Confirm Add Time",
            f"Add {time_display} to your completed hours?\n\nThis will reduce your remaining time by {time_display}."
        )
        
        if result:
            global remaining_seconds
            remaining_seconds = max(0, remaining_seconds - manual_seconds)
            hours_remaining = remaining_seconds / 3600
            hours_label.configure(text=f"{hours_remaining:.2f}")
            progress_percentage = (remaining_seconds / (total_hours_required * 3600)) * 100
            try:
                radbar2.set(progress_percentage)
            except:
                pass
            save_data()
            manual_time_entry.delete(0, 'end')
            manual_time_entry2.delete(0, 'end')
            manual_time_entry3.delete(0, 'end')
            hours_completed = (total_hours_required * 3600 - remaining_seconds) / 3600
            messagebox.showinfo(
                "Time Added Successfully", 
                f"Added {time_display} to your completed time!\n\nTotal completed: {hours_completed:.2f} hours\nRemaining: {hours_remaining:.2f} hours"
            )
        
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers only!\n\nExample: Hours=2, Minutes=30, Seconds=15")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while adding time: {e}")
def button_click():
    messagebox.showinfo("Button Clicked", "You clicked the button!")
    
button1 = ctk.CTkButton(frame3d_in, width=80, text="CLOCK IN", command=clock_in_button, fg_color="#4CAF50", hover_color="#45a049", corner_radius=0)
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = ctk.CTkButton(frame3d_in, width=70, height=30, text="CLOCK OUT", command=clock_out_button, fg_color="#f44336", hover_color="#d32f2f", corner_radius=0)
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = ctk.CTkButton(frame3d_in, width=80, text="BREAK", command=breakOut, fg_color="#FF9800", hover_color="#F57C00", corner_radius=0)
button3.grid(row=1, column=0, padx=10, pady=10)

button4 = ctk.CTkButton(frame3d_in, width=80, text="RESET", command=rest_button_click, fg_color="#9E9E9E", hover_color="#757575", corner_radius=0)
button4.grid(row=1, column=1, padx=10, pady=10)

button5 = ctk.CTkButton(button_frame2, width=80, text="ADD TIME", command=add_manual_time, fg_color="#174F7C", hover_color="#2365A8")
button5.pack(padx=10, pady=10)


#CALENDAR
def open_calendar():
    
    global calendar_window
    
    if calendar_window is not None and calendar_window.winfo_exists():
        calendar_window.lift()
        return
    
    calendar_window = Toplevel(app)
    calendar_window.title("Select Date")
    calendar_window.geometry("300x350")
    calendar_window.configure(bg="#2b2b2b")  # Dark background for window
        
    app.update_idletasks()
    x = app.winfo_x()
    y = app.winfo_y()
    width = app.winfo_width()
    calendar_window.geometry(f"+{x + width + 10}+{y}")
    
    cal = Calendar(
        calendar_window, 
        selectmode='day',
        background="#2b2b2b",
        foreground="white",
        headersbackground="#1f6aa5",
        weekendbackground="#3b0f6d",
        weekendforeground="white",
        selectbackground="#FF00BF",
        selectforeground="white",
        normalbackground="#2b2b2b",
        normalforeground="white",
        bordercolor="#2b2b2b",
        othermonthforeground="gray",
        othermonthbackground="#2c3ab8",
        othermonthweforeground="gray",
        othermonthwebackground="#033270"
    )
    calendar_window.transient(app)
    calendar_window.grab_set()
    cal.pack(pady=20)
    
    def open_note_for_selected_date():
        """Open note window for the currently selected date"""
        selected_date = cal.get_date()
        open_note_window(selected_date, cal)
    
    def str_to_date(date_str):
        """Convert MM/dd/yy string to datetime.date object"""
        try:
            return datetime.strptime(date_str, "%m/%d/%y").date()
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return datetime.strptime(date_str, "%m/%d/%Y").date()
    
    def date_to_str(date_obj):
        """Convert datetime.date object to MM/dd/yy string"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime("%m/%d/%y")
    
    def set_status(status, color):
        selected_date_str = cal.get_date()
        selected_date_obj = str_to_date(selected_date_str)
        daily_status[selected_date_str] = status
        for event_id in cal.get_calevents(selected_date_obj):
            cal.calevent_remove(event_id)
        cal.calevent_create(selected_date_obj, status, status)
        cal.tag_config(status, background=color, foreground="white")
        save_data()  
    
    def clear_status():
        selected_date_str = cal.get_date()
        selected_date_obj = str_to_date(selected_date_str)
        if selected_date_str in daily_status:
            del daily_status[selected_date_str]
        for event_id in cal.get_calevents(selected_date_obj):
            cal.calevent_remove(event_id)
        save_data()
    
    select_button = ctk.CTkButton(calendar_window, text="Select", command=open_note_for_selected_date)
    select_button.pack(pady=10, padx=10)
    
    status_buttons_frame = ctk.CTkFrame(calendar_window, fg_color="transparent")
    status_buttons_frame.pack(pady=5)
    
    present_button = ctk.CTkButton(
        status_buttons_frame, 
        text="Present", 
        width=80, 
        height=30,
        command=lambda: set_status("Present", "#4CAF50"),
        fg_color="#4CAF50",
        hover_color="#45a049"
    )
    present_button.grid(row=0, column=0, padx=5, pady=2)
    
    late_button = ctk.CTkButton(
        status_buttons_frame, 
        text="Late", 
        width=80, 
        height=30,
        command=lambda: set_status("Late", "#FF9800"),
        fg_color="#FF9800",
        hover_color="#F57C00"
    )
    late_button.grid(row=0, column=1, padx=5, pady=2)
    
    absent_button = ctk.CTkButton(
        status_buttons_frame, 
        text="Absent", 
        width=80, 
        height=30,
        command=lambda: set_status("Absent", "#f44336"),
        fg_color="#f44336",
        hover_color="#d32f2f"
    )
    absent_button.grid(row=1, column=0, padx=5, pady=2)
    
    clear_button = ctk.CTkButton(
        status_buttons_frame, 
        text="Clear Status", 
        width=80, 
        height=30,
        command=clear_status,
        fg_color="#9E9E9E",
        hover_color="#757575"
    )
    clear_button.grid(row=1, column=1, padx=5, pady=2)

    for date_str, status in daily_status.items():
        try:
            date_obj = str_to_date(date_str)
            color_map = {
                "Present": "#4CAF50",
                "Late": "#FF9800", 
                "Absent": "#f44336"
            }
            color = color_map.get(status, "#4CAF50")
            cal.calevent_create(date_obj, status, status)
            cal.tag_config(status, background=color, foreground="white")
        except Exception as e:
            print(f"Error loading status for date {date_str}: {e}")
    
    def open_note_window(date, calendar):
        global note_window
        
        if note_window is not None and note_window.winfo_exists():
            note_window.destroy()
        
        note_window = Toplevel(calendar_window)
        note_window.title(f"Notes for {date}")
        note_window.geometry("300x250")
        note_window.configure(bg="#2b2b2b") 
        
        app.update_idletasks()
        x = calendar.winfo_rootx()
        y = calendar.winfo_rooty()
        width = calendar.winfo_width()
        note_window.geometry(f"+{x + width + 10}+{y}")
        
        note_text = ctk.CTkTextbox(note_window, width=280, height=150)
        note_text.pack(pady=10, padx=10)
        
        existing_note = daily_notes.get(date, "")
        note_text.insert("0.0", existing_note)
        
        def save_note():
            daily_notes[date] = note_text.get("0.0", "end").strip()
            save_data() 
            note_window.destroy()
    
        save_button = ctk.CTkButton(note_window, text="Save Note", command=save_note)
        save_button.pack(pady=5)
        
        def delete_note():
            result = messagebox.askyesno("Delete Note", f"Are you sure you want to delete the note for {date}?")
            if result:
                if date in daily_notes:
                    del daily_notes[date]
                save_data()
                messagebox.showinfo("Note Deleted", f"Note for {date} has been deleted.")
                note_window.destroy()
        
        delete_button = ctk.CTkButton(note_window, text="Delete Note", command=delete_note, fg_color="#f44336", hover_color="#d32f2f")
        delete_button.pack(pady=5)

button6 = at.Button3d(app, width=10, text="CALENDAR", command=open_calendar)
button6.place(relx=0.62, rely=0.1, anchor="e")

#FUNCTIONS

is_clocked_in = False
is_on_break = False

total_hours_required = 300
remaining_seconds = total_hours_required * 60 * 60

def save_data(include_close_time=False):
    """Save current state to ojt_data.json"""
    try:
        data = {
            "remaining_seconds": remaining_seconds,
            "is_clocked_in": is_clocked_in,
            "is_on_break": is_on_break,
            "total_hours_required": total_hours_required,
            "daily_notes": daily_notes,
            "daily_status": daily_status
        }
        
        if include_close_time:
            data["last_closed"] = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
            
        with open("ojt_data.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    """Load saved state from ojt_data.json"""
    global remaining_seconds, is_clocked_in, is_on_break, total_hours_required, daily_notes, daily_status
    
    try:
        if os.path.exists("ojt_data.json"):
            with open("ojt_data.json", "r") as f:
                data = json.load(f)
            
            remaining_seconds = data.get("remaining_seconds", total_hours_required * 3600)
            is_clocked_in = data.get("is_clocked_in", False)
            is_on_break = data.get("is_on_break", False)
            total_hours_required = data.get("total_hours_required", 300)
            daily_notes = data.get("daily_notes", {})
            daily_status = data.get("daily_status", {})
            
            last_closed = data.get("last_closed", None)
            if last_closed:
                last_closed_label.configure(text=f"Last closed: {last_closed}")
            else:
                last_closed_label.configure(text="Never closed")
            
            update_ui_from_data()
            print("Data loaded successfully")
        else:
            last_closed_label.configure(text="Never closed")
            print("No save file found, starting fresh")
    except Exception as e:
        last_closed_label.configure(text="Error loading data")
        print(f"Error loading data: {e}")

def update_ui_from_data():
    """Update UI elements to reflect loaded data"""
    hours_remaining = remaining_seconds / 3600
    hours_label.configure(text=f"{hours_remaining:.2f}")
    progress_percentage = (remaining_seconds / (total_hours_required * 3600)) * 100
    try:
        radbar2.set(progress_percentage)
    except:
        pass
    if is_clocked_in:
        if is_on_break:
            status_label.configure(text="Status: On Break", text_color="#FF9800")
        else:
            status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
    else:
        status_label.configure(text="Status: Clocked Out", text_color="#f44336")

def on_closing():
    """Handle app closing with confirmation"""
    result = messagebox.askyesno(
        "Exit Confirmation", 
        "Are you sure you want to close the OJT Tracker?\n\nYou will be automatically clocked out and your progress will be saved."
    )
    
    if result:
        global is_clocked_in, is_on_break
        if is_clocked_in:
            is_clocked_in = False
            is_on_break = False
            print("Automatically clocked out on app close")
            
        save_data(include_close_time=True)
        cleanup_lock_file()  # Clean up lock file before closing
        app.destroy()

def update_datetime():
    global remaining_seconds, is_clocked_in, is_on_break
    
    now = datetime.now()
    current_time = now.strftime("%B %d, %Y\n%I:%M:%S %p")
    datetime_label.configure(text=current_time)
    
    if is_clocked_in and not is_on_break and remaining_seconds > 0:
        remaining_seconds -= 1
        hours_remaining = remaining_seconds / 3600
        hours_label.configure(text=f"{hours_remaining:.2f}")
        
        progress_percentage = (remaining_seconds / (total_hours_required * 3600)) * 100
        try:
            radbar2.set(progress_percentage) 
        except:
            pass
        
        if remaining_seconds % 60 == 0:
            save_data()
            
    elif remaining_seconds <= 0:
        hours_label.configure(text="0.00")
        try:
            radbar2.set(0)  
        except:
            pass
   
        
    datetime_label.after(1000, update_datetime)

datetime_label.pack(pady=10)

def clock_in():
    global is_clocked_in, is_on_break
    if not is_clocked_in:
        is_clocked_in = True
        is_on_break = False
        status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
        save_data()
    else:
        messagebox.showinfo("Already Clocked In", "You are already clocked in.")
        
def clock_out():
    global is_clocked_in, is_on_break
    if is_clocked_in:
        is_clocked_in = False
        is_on_break = False
        status_label.configure(text="Status: Clocked Out", text_color="#f44336")
        save_data() 
    else:
        messagebox.showinfo("Not Clocked In", "You are not clocked in.")

def breakOut():
    global is_clocked_in, is_on_break
    if is_clocked_in and not is_on_break:
        is_on_break = True
        status_label.configure(text="Status: On Break", text_color="#FF9800")
        save_data() 
    elif is_on_break:
        is_on_break = False
        status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
        save_data() 
    else:
        messagebox.showinfo("Cannot Take Break", "You must be clocked in to take a break.") 
        
def resethrs():
    global remaining_seconds
    
    result = messagebox.askyesno(
        "Confirm Reset", 
        "Are you sure you want to reset your hours to 300.00?\n\nThis action cannot be undone!"
    )
    
    if result:  
        remaining_seconds = total_hours_required * 3600
        hours_label.configure(text=f"{total_hours_required:.2f}")
        try:
            radbar2.set(100)
        except:
            pass
        save_data()  
        messagebox.showinfo("Reset Complete", "Hours have been reset to 300.00")
        
# MANUAL TIME ENTRY
def validate_numeric_input(char):
    """Validate that input is numeric only"""
    return char.isdigit() or char == ""
vcmd = (app.register(validate_numeric_input), '%S')

manual_time_entry = ctk.CTkEntry(
    manual_time_frame, 
    width=35, 
    placeholder_text="HH", 
    justify="center",
    validate="key",
    validatecommand=vcmd
)
manual_time_entry.grid(row=0, column=0, padx=3, pady=5)

manual_time_entry2 = ctk.CTkEntry(
    manual_time_frame, 
    width=35, 
    placeholder_text="MM", 
    justify="center",
    validate="key",
    validatecommand=vcmd
)
manual_time_entry2.grid(row=0, column=1, padx=3, pady=5)

manual_time_entry3 = ctk.CTkEntry(
    manual_time_frame, 
    width=35, 
    placeholder_text="SS", 
    justify="center",
    validate="key",
    validatecommand=vcmd
)
manual_time_entry3.grid(row=0, column=2, padx=3, pady=5)

load_data()
app.protocol("WM_DELETE_WINDOW", on_closing)
update_datetime()
app.update()
app.mainloop()
