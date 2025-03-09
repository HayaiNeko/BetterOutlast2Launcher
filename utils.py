import os
import subprocess
import tkinter as tk
from tkinter import messagebox


def show_error(message):
    """Display a messagebox for errors"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message, parent=root)
    root.destroy()

def create_junction(source, target):
    if os.name == "nt": #On Windows
        command = f'mklink /J "{target}" "{source}"'
        result = subprocess.run(command, shell = True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"[INFO] Junction created: {target} -> {source}")
        else:
            raise OSError(f"Failed to create junction: {result.stderr.strip()}")
    else:
        try:
            os.symlink(source, target, target_is_directory=True)
            print(f"[INFO] Junction created: {target} -> {source}")
        except Exception as e:
            raise OSError(f"Failed to create junction: {e}")


