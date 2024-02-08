import os
import json
from tkinter import Tk, Button, Label, Listbox, Toplevel, Frame, filedialog
from pdfminer.high_level import extract_text

# Initialize the variables with default values
uploaded_files = []  # Keep track of uploaded file paths
job_stages_state = {}  # Key: job name, Value: selected stage

# Initial data load
def load_data():
    global uploaded_files, job_stages_state
    try:
        with open('job_data.json', 'r') as f:
            data = json.load(f)
            uploaded_files = data.get('uploaded_files', [])
            job_stages_state = data.get('job_stages_state', {})
    except FileNotFoundError:
        # File not found, no data to load, variables retain their initial values
        print("No existing data file found. Starting fresh.")

def save_data():
    data = {
        'uploaded_files': uploaded_files,
        'job_stages_state': job_stages_state
    }
    with open('job_data.json', 'w') as f:
        json.dump(data, f)

# Load data at the start
load_data()

def add_pdf():
    filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not filepath:
        return
    
    uploaded_files.append(filepath)
    extract_and_display_job_names(filepath)

def extract_and_display_job_names(filepath):
    try:
        text = extract_text(filepath)
        job_names = [line.split("Name:", 1)[1].strip() for line in text.split('\n') if "Name:" in line]

        if job_names:
            formatted_name = job_names[0] if len(job_names) == 1 else f"{job_names[1]} - {job_names[0]}"
            job_name_listbox.insert('end', formatted_name)
        else:
            job_name_listbox.insert('end', "No Job Name Found")

    except Exception as e:
        job_name_listbox.insert('end', f"Error reading PDF: {e}")

def on_file_click(event):
    widget = event.widget
    selection = widget.curselection()
    if selection:
        index = selection[0]
        job_name = widget.get(index)
        
        action_window = Toplevel(root)
        action_window.title(f"Actions for {job_name}")
        action_window.geometry("600x400")

        stages_frame = Frame(action_window)
        stages_frame.pack(pady=20)

        stages = ["ESTIMATING", "DESIGN", "CUTTING", "ASSEMBLY", "INSTALL", "PICKUP", "TOUCHUPS"]
        for stage in stages:
            btn = Button(stages_frame, text=stage, command=lambda s=stage, f=stages_frame: select_stage(job_name, s, f))
            btn.pack(side='left', padx=5)
            if job_name in job_stages_state and job_stages_state[job_name] == stage:
                btn.config(bg='lightblue')
        
        # Save button to explicitly save current state
        save_button = Button(action_window, text="Save", command=save_data)
        save_button.pack(side='bottom', pady=10)

def select_stage(job_name, stage, frame):
    job_stages_state[job_name] = stage
    # Update buttons to reflect the selected stage
    for widget in frame.winfo_children():
        if widget.cget('text') == stage:
            widget.config(bg='lightblue')
        else:
            widget.config(bg='SystemButtonFace')

def on_close():
    save_data()
    root.destroy()

root = Tk()
root.title("PDF Job Name Extractor")
root.geometry("900x600")

add_pdf_button = Button(root, text="Add PDF", command=add_pdf)
add_pdf_button.pack(pady=20)

job_name_listbox = Listbox(root, height=10, width=50, activestyle='dotbox')
job_name_listbox.pack(pady=20)
job_name_listbox.bind('<<ListboxSelect>>', on_file_click)

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()