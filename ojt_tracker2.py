import customtkinter as ctk
import tkinter as tk
import awesometkinter as at
import json
import os

from cProfile import label
from tkinter import ttk, messagebox
from datetime import datetime


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

button_frame = ctk.CTkFrame(app, width=300, height=100, corner_radius=10, fg_color="#242424")
button_frame.place(relx=0.05, rely=0.8, anchor="w")
button_frame.grid_propagate(True)

button_frame2 = ctk.CTkFrame(app, width=100, height=50, corner_radius=10, fg_color="#242424")
button_frame2.place(relx=0.90, rely=0.74, anchor="e")

manual_time_frame = ctk.CTkFrame(app, width=120, height=30, corner_radius=10, fg_color="#242424")
manual_time_frame.place(relx=0.93, rely=0.86, anchor="e")

datetime_frame = ctk.CTkFrame(app, width=150, height=30, corner_radius=10, fg_color="#242424")
datetime_frame.place(relx=0.14, rely=0.45, anchor="w")

# LABELS
hours_label = ctk.CTkLabel(hours_frame, text="300.00", font=ctk.CTkFont(size=50, weight="bold"))
hours_label.pack(pady=1)

status_label = ctk.CTkLabel(status_frame, text="Status: Clocked Out", font=ctk.CTkFont(size=14))
status_label.pack(pady=5)

datetime_label = ctk.CTkLabel(
    datetime_frame, 
    text="Date and Time", 
    font=ctk.CTkFont(size=14, weight="bold"), 
    text_color="white")

# PROGRESS BAR
# Suppress IDE warning for RadialProgressbar
try:
    radbar2 = at.RadialProgressbar(app, fg='green', parent_bg="#242424", size=(150,150))  # type: ignore
    radbar2.place(relx=0.95, rely=0.37, anchor="e")
    radbar2.set(100)  # Start at 100% since we start with full 300 hours
except AttributeError:
    # Fallback if RadialProgressbar is not available
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
    

def button_click():
    messagebox.showinfo("Button Clicked", "You clicked the button!")
    
button1 = ctk.CTkButton(button_frame, width=80, text="CLOCK IN", command=clock_in_button, fg_color="#4CAF50", hover_color="#45a049")
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = ctk.CTkButton(button_frame, width=70, height=30, text="CLOCK OUT", command=clock_out_button, fg_color="#f44336", hover_color="#d32f2f")
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = ctk.CTkButton(button_frame, width=80, text="BREAK", command=breakOut, fg_color="#FF9800", hover_color="#F57C00")
button3.grid(row=1, column=0, padx=10, pady=10)

button4 = ctk.CTkButton(button_frame, width=80, text="RESET", command=rest_button_click, fg_color="#9E9E9E", hover_color="#757575")
button4.grid(row=1, column=1, padx=10, pady=10)

button5 = ctk.CTkButton(button_frame2, width=80, text="ADD TIME", command=button_click, fg_color="#174F7C", hover_color="#2365A8")
button5.pack(padx=10, pady=10)

#FUNCTIONS

is_clocked_in = False
is_on_break = False

total_hours_required = 300
remaining_seconds = total_hours_required * 60 * 60

# Data persistence functions
def save_data():
    """Save current state to ojt_data.json"""
    try:
        data = {
            "remaining_seconds": remaining_seconds,
            "is_clocked_in": is_clocked_in,
            "is_on_break": is_on_break,
            "total_hours_required": total_hours_required
        }
        with open("ojt_data.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    """Load saved state from ojt_data.json"""
    global remaining_seconds, is_clocked_in, is_on_break, total_hours_required
    
    try:
        if os.path.exists("ojt_data.json"):
            with open("ojt_data.json", "r") as f:
                data = json.load(f)
            
            remaining_seconds = data.get("remaining_seconds", total_hours_required * 3600)
            is_clocked_in = data.get("is_clocked_in", False)
            is_on_break = data.get("is_on_break", False)
            total_hours_required = data.get("total_hours_required", 300)
            
            # Update UI to reflect loaded state
            update_ui_from_data()
            print("Data loaded successfully")
        else:
            print("No save file found, starting fresh")
    except Exception as e:
        print(f"Error loading data: {e}")

def update_ui_from_data():
    """Update UI elements to reflect loaded data"""
    # Update hours display
    hours_remaining = remaining_seconds / 3600
    hours_label.configure(text=f"{hours_remaining:.2f}")
    
    # Update progress bar
    progress_percentage = (remaining_seconds / (total_hours_required * 3600)) * 100
    try:
        radbar2.set(progress_percentage)
    except:
        pass
    
    # Update status display
    if is_clocked_in:
        if is_on_break:
            status_label.configure(text="Status: On Break", text_color="#FF9800")
        else:
            status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
    else:
        status_label.configure(text="Status: Clocked Out", text_color="#f44336")

def update_datetime():
    global remaining_seconds, is_clocked_in, is_on_break
    
    now = datetime.now()
    current_time = now.strftime("%B %d, %Y\n%I:%M:%S %p")
    datetime_label.configure(text=current_time)
    
    # Only countdown when clocked in and not on break
    if is_clocked_in and not is_on_break and remaining_seconds > 0:
        remaining_seconds -= 1  # Decrease by 1 second only when working
        hours_remaining = remaining_seconds / 3600  # Convert to hours for display only
        hours_label.configure(text=f"{hours_remaining:.2f}")
        
        # Sync progress bar to show remaining hours (decreases as hours decrease)
        progress_percentage = (remaining_seconds / (total_hours_required * 3600)) * 100
        try:
            radbar2.set(progress_percentage)  # Progress bar decreases with hours
        except:
            pass
        
        # Save progress every minute (60 seconds) to avoid too frequent writes
        if remaining_seconds % 60 == 0:
            save_data()
            
    elif remaining_seconds <= 0:
        hours_label.configure(text="0.00")
        try:
            radbar2.set(0)  # Progress bar at 0 when no hours left
        except:
            pass
    # If not clocked in or on break, just update datetime without countdown
        
    datetime_label.after(1000, update_datetime)

datetime_label.pack(pady=10)

def clock_in():
    global is_clocked_in, is_on_break
    if not is_clocked_in:
        is_clocked_in = True
        is_on_break = False
        status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
        save_data()  # Save state change
    else:
        messagebox.showinfo("Already Clocked In", "You are already clocked in.")
        
def clock_out():
    global is_clocked_in, is_on_break
    if is_clocked_in:
        is_clocked_in = False
        is_on_break = False
        status_label.configure(text="Status: Clocked Out", text_color="#f44336")
        save_data()  # Save state change
    else:
        messagebox.showinfo("Not Clocked In", "You are not clocked in.")

def breakOut():
    global is_clocked_in, is_on_break
    if is_clocked_in and not is_on_break:
        is_on_break = True
        status_label.configure(text="Status: On Break", text_color="#FF9800")
        save_data()  # Save state change
    elif is_on_break:
        is_on_break = False
        status_label.configure(text="Status: Clocked In", text_color="#4CAF50")
        save_data()  # Save state change
    else:
        messagebox.showinfo("Cannot Take Break", "You must be clocked in to take a break.") 
        
def resethrs():
    global remaining_seconds
    
    # Always ask for confirmation before resetting
    result = messagebox.askyesno(
        "Confirm Reset", 
        "Are you sure you want to reset your hours to 300.00?\n\nThis action cannot be undone!"
    )
    
    if result:  # User clicked "Yes"
        remaining_seconds = total_hours_required * 3600  # Reset to initial total hours in seconds
        hours_label.configure(text=f"{total_hours_required:.2f}")
        try:
            radbar2.set(100)  # Reset progress bar to full
        except:
            pass
        save_data()  # Save reset state
        messagebox.showinfo("Reset Complete", "Hours have been reset to 300.00")
    # If user clicked "No", do nothing (function ends)

# MANUAL TIME ENTRY
manual_time_entry = ctk.CTkEntry(manual_time_frame, width=35, placeholder_text="HH", justify="center")
manual_time_entry.grid(row=0, column=0, padx=3, pady=5)

manual_time_entry2 = ctk.CTkEntry(manual_time_frame, width=35, placeholder_text="MM", justify="center")
manual_time_entry2.grid(row=0, column=1, padx=3, pady=5)

manual_time_entry3 = ctk.CTkEntry(manual_time_frame, width=35, placeholder_text="SS" , justify="center")
manual_time_entry3.grid(row=0, column=2, padx=3, pady=5)

# Load saved data on startup
load_data()

# Set up proper close handler before starting mainloop
app.protocol("WM_DELETE_WINDOW", lambda: [save_data(), app.destroy()])

update_datetime()
app.update()
app.mainloop()
