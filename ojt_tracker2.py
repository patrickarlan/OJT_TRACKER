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
    radbar2 = at.RadialProgressbar(app, fg='green', parent_bg="#242424", size=(150,150))
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
    
button1 = ctk.CTkButton(button_frame, width=80, text="CLOCK IN", command=clock_in_button, fg_color="#4CAF50", hover_color="#45a049")
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = ctk.CTkButton(button_frame, width=70, height=30, text="CLOCK OUT", command=clock_out_button, fg_color="#f44336", hover_color="#d32f2f")
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = ctk.CTkButton(button_frame, width=80, text="BREAK", command=breakOut, fg_color="#FF9800", hover_color="#F57C00")
button3.grid(row=1, column=0, padx=10, pady=10)

button4 = ctk.CTkButton(button_frame, width=80, text="RESET", command=rest_button_click, fg_color="#9E9E9E", hover_color="#757575")
button4.grid(row=1, column=1, padx=10, pady=10)

button5 = ctk.CTkButton(button_frame2, width=80, text="ADD TIME", command=add_manual_time, fg_color="#174F7C", hover_color="#2365A8")
button5.pack(padx=10, pady=10)

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
            "total_hours_required": total_hours_required
        }
        
        if include_close_time:
            data["last_closed"] = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
            
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
