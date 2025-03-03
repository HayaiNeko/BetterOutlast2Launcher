import customtkinter as ctk
from tkinter import filedialog

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:  # Check if a folder was selected
        entry_var.set(folder_selected)
    return folder_selected

# Create the main application window
app = ctk.CTk()
app.title("Folder Picker")
app.geometry("500x200")

# Label
label = ctk.CTkLabel(app, text="Select a folder:")
label.pack(pady=10)

# Entry to display selected folder
entry_var = ctk.StringVar()
entry = ctk.CTkEntry(app, textvariable=entry_var, width=400)
entry.pack(pady=10)

# Button to open file explorer
button = ctk.CTkButton(app, text="Browse", command=select_folder)
button.pack(pady=10)

# Run the application
app.mainloop()
