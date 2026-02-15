import os
import sys
from time import strftime
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

#funtions of the OJT TRACKER
required_hours = 300
worked_seconds = 0
clock_in_time = None
is_clocked_in = False

#data_file = "ojt_data.txt"
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    
data_file = os.path.join(application_path, "ojt_data.txt")


worked_seconds = 0
last_closed_time = "Never"

if os.path.exists(data_file):
    with open(data_file, "r") as f:
        lines = f.readlines()
        worked_seconds = float(lines[0].strip())
        last_closed_time = lines[1].strip()
else:
    worked_seconds = 0
    last_closed_time = "Never"

# try:
#     with open(data_file, "r") as f:
#         lines = f.readlines()
#         worked_seconds = float(lines[0].strip())
#         last_closed_time = lines[1].strip()
# except FileNotFoundError:
#     worked_seconds = 0
#     last_closed_time = "Never"

root = tk.Tk()
root.title("OJT Tracker")
#root.geometry("400x400")

def only_numbers(char):
    return char.isdigit() or char == ""

vcmd = root.register(only_numbers)


window_width = 400
window_height = 500

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

#houes label
hours_box = tk.Label(
    root, 
    text="300 HOURS", 
    font=("Arial", 20), 
    bd=2, 
    relief="solid")
hours_box.pack(pady=40)

time_label = tk.Label(
    root,
    font= ("Arial", 14)
)
time_label.pack(pady=10)

status_label = tk.Label(root, text="Status: Clocked Out", font=("Arial", 12))
status_label.pack(pady=5)

closed_label = tk.Label(root, text=f"App last closed at:\n{last_closed_time}", font=("Arial", 9))
closed_label.pack(pady=5)

def on_close():
    with open(data_file, "w") as f:
        f.write(str(worked_seconds) + "\n")
        f.write(datetime.now().strftime("%B %d, %Y %I:%M:%S %p"))
    root.destroy()

#date and time function
def update_time():
    global worked_seconds, is_clocked_in
    
    now = datetime.now()
    current_time = now.strftime("%B %d, %Y %I:%M:%S %p")
    time_label.config(text=current_time)
    
    if is_clocked_in:
        worked_seconds += 1
        
    worked_hours = worked_seconds / 3600
    remaining_hours = required_hours - worked_hours
    
    if remaining_hours < 0:
        remaining_hours = 0
        is_clocked_in = False
        
    hours_box.config(text=f"{remaining_hours:.2f} HOURS")     
    
    percent = (remaining_hours / required_hours) * 100
    progres["value"] = percent
    
    root.after(1000, update_time) 


#progress bar
progres = ttk.Progressbar(root, length=300, mode='determinate')
progres.pack(pady=10)
progres["maximum"] = 100
progres["value"] = 100

def on_close():
    confirm = messagebox.askyesno("Exit", "Are you sure you want to exit?")
    
    if not confirm:
        return
    
    with open(data_file, "w") as f:
        f.write(str(worked_seconds) + "\n")
        f.write(datetime.now().strftime("%B %d, %Y %I:%M:%S %p"))
        
    root.destroy()    

def clock_in():
    global clock_in_time, is_clocked_in
    
    if not is_clocked_in:
        clock_in_time = datetime.now()
        is_clocked_in = True
        
        clock_in_button.config(bg="green")
        status_label.config(text="Status: Clocked In")

def clock_out():
    global is_clocked_in
    
    if is_clocked_in:
        is_clocked_in = False
        clock_in_button.config(bg="SystemButtonFace")
        status_label.config(text="Status: Clocked Out")

def reset_hours():
    global worked_seconds, clock_in_time, is_clocked_in
    
    confirm = messagebox.askyesno("Reset", "Are you sure you want to reset progress?")
    if not confirm:
        return

    worked_seconds = 0
    is_clocked_in = False
    clock_in_time = None

    status_label.config(text="Status: Clocked Out")
    clock_in_button.config(bg="SystemButtonFace")

    # Immediately update display to 300
    hours_box.config(text="300.00 HOURS")
    progres["value"] = 100
    
    
def add_manual_time():
    global worked_seconds
    
    try:
        hours = int(hour_entry.get() or 0)
        minutes = int(minute_entry.get() or 0)
        seconds = int(second_entry.get() or 0)
        
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        worked_seconds += total_seconds
        
        hour_entry.delete(0, tk.END)
        minute_entry.delete(0, tk.END)
        second_entry.delete(0, tk.END)
        
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for hours, minutes, and seconds.")

#BUTTONS

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

reset_button = tk.Button(button_frame, text="Reset Hours", bg="red", fg="white", command=reset_hours)
reset_button.pack(padx=5)

clock_in_button = tk.Button(button_frame, text="Clock In", command=clock_in)
clock_in_button.pack(pady=5)

clock_out_button = tk.Button(button_frame, text="Clock Out", command=clock_out)
clock_out_button.pack(padx=5)

#ENTRY WIDGETS (HOURS, MINUTES, SECONDS)

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

hour_entry = tk.Entry(input_frame, width=5, validate="key", validatecommand=(vcmd, "%P"))
hour_entry.grid(row=0, column=0)

minute_entry = tk.Entry(input_frame, width=5, validate="key", validatecommand=(vcmd, "%P"))
minute_entry.grid(row=0, column=2)

second_entry = tk.Entry(input_frame, width=5, validate="key", validatecommand=(vcmd, "%P"))
second_entry.grid(row=0, column=4)

add_time_button = tk.Button(root, text="Add Time", command=add_manual_time)
add_time_button.pack(pady=10)

# Labels under entries
tk.Label(input_frame, text="H").grid(row=1, column=0)
tk.Label(input_frame, text="M").grid(row=1, column=2)
tk.Label(input_frame, text="S").grid(row=1, column=4)

update_time()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()