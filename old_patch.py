import os
import time
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui import fonts, colors

# 🔹 Chemins et IDs
APP_ID = "414700"  # Outlast 2
DEPOT_ID = "414701"  # Fichiers Windows
MANIFEST_ID = "7085410466650398118"  # Version du 10 mai 2017

# 🔹 Dossier Steam par défaut
STEAM_CONTENT_PATH = rf"C:\Program Files (x86)\Steam\steamapps\content\app_{APP_ID}\depot_{DEPOT_ID}"

class OldPatch:
    def __init__(self, saved_path=None):
        """
        Initializes the Old Patch manager.
        - Checks if a path has already been saved.
        - Automatically searches for the Old Patch folder if necessary.
        - Validates that Outlast2.bat is present in the detected directory.
        """
        if saved_path and self.is_valid_old_patch(saved_path):
            self.path = saved_path
        else:
            detected_path = self.detect_path()
            self.path = detected_path if self.is_valid_old_patch(detected_path) else None

    def detect_path(self):
        """
        Automatically detects the Old Patch folder based on the program's location.
        """
        program_path = os.path.dirname(os.path.abspath(__file__))
        common_folder = os.path.join("steamapps", "common", "Outlast 2")

        if not program_path.endswith(common_folder):
            return None  # Unable to determine the location

        steamapps_root = program_path[:-len(common_folder)].rstrip(os.sep)
        old_patch_path = os.path.join(steamapps_root, "steamapps", "content", "app_414700", "depot_414701")

        return old_patch_path if os.path.isdir(old_patch_path) else None

    def is_valid_old_patch(self, path):
        """
        Checks if the given path contains Outlast2.bat, meaning it's a valid Old Patch directory.
        """
        if path and os.path.isdir(path):
            bat_file_path = os.path.join(path, "Outlast2.bat")
            return os.path.isfile(bat_file_path)
        return False

    def get_old_patch(self, root):
        """
        Allows the user to either:
        - Select a folder manually.
        - Download the Old Patch through Steam with progress tracking.
        """
        self.window = ctk.CTkToplevel(root, fg_color=colors["background"])
        self.window.title("Old Patch Download")
        self.window.attributes("-topmost", True)
        self.window.geometry("500x300")

        ctk.CTkLabel(self.window, text="Select your Old Patch folder:",
                     font=fonts["h4"], text_color=colors["text"]).pack(pady=10)

        ctk.CTkButton(self.window, text="📂 Select Folder", command=self.select_folder,
                      font=fonts["text"], text_color=colors["text"], fg_color=colors["primary"],
                      hover_color=colors["primary hover"]).pack(pady=5)

        ctk.CTkLabel(self.window, text="Or download via Steam:",
                     font=fonts["h4"], text_color=colors["text"]).pack(pady=10)

        ctk.CTkButton(self.window, text="🎮 Open Steam Console", command=self.open_steam_console,
                      font=fonts["text"], text_color=colors["text"], fg_color=colors["primary"],
                      hover_color=colors["primary hover"]).pack(pady=5)

        self.copy_steam_command_button = ctk.CTkButton(self.window, text="📋 Copy Steam Download Command", command=self.copy_steam_command,
                                                       font=fonts["text"], text_color=colors["text"], fg_color=colors["primary"],
                                                       hover_color=colors["primary hover"])
        self.copy_steam_command_button.pack(pady=5)

        self.progress_label = ctk.CTkLabel(self.window, text="📥 Progress: 0.00%",
                                           font=fonts["small"], text_color=colors["text"])
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.window, progress_color=colors["primary"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        # Start tracking download in a separate thread to avoid UI freezing
        threading.Thread(target=self.track_download).start()

        self.window.mainloop()

    def select_folder(self):
        """
        Allows the user to manually select a folder for the Old Patch.
        """
        folder_selected = filedialog.askdirectory(title="Select Old Patch Folder")
        if folder_selected:
            self.path = folder_selected
            messagebox.showinfo("Success", f"Old Patch folder selected:\n{self.path}")
            self.window.destroy()

    def open_steam_console(self):
        """
        Opens the Steam console.
        """
        subprocess.run("start steam://open/console", shell=True)

    def copy_steam_command(self):
        """
        Copies the Steam download command to the clipboard.
        """
        self.window.clipboard_clear()
        self.window.clipboard_append(f"download_depot {APP_ID} {DEPOT_ID} {MANIFEST_ID}")
        self.window.update()
        self.copy_steam_command_button.configure(text="✅ Copy Steam Download Command")

    def track_download(self):
        """
        Tracks the download progress of the Old Patch.
        """
        expected_size = 27096937514  # Approximate expected size in bytes
        expected_size_gb = expected_size / (1024**3)  # Convert to GB

        while not os.path.exists(STEAM_CONTENT_PATH):
            self.progress_label.configure(text="📥 Waiting for download to start...", text_color="orange")
            time.sleep(1)
        try:
            while True:
                total_size = self.get_folder_size(STEAM_CONTENT_PATH)
                progress = min(100.0, (total_size / expected_size) * 100)  # Capped at 100%

                self.progress_label.configure(
                    text=f"📥 Progress: {progress:.2f}% ({total_size / (1024**3):.2f} GB / {expected_size_gb:.2f} GB)"
                )
                self.progress_bar.set(progress / 100)

                if total_size >= expected_size:
                    self.progress_label.configure(text="✅ Download complete!", text_color="green")
                    self.path = STEAM_CONTENT_PATH
                    break
                time.sleep(1)

        except Exception as e:
            print(e)

    @staticmethod
    def get_folder_size(path):
        """
        Calculates the total size of a folder.
        """
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except Exception as e:
                    print(f"Error on {fp}: {e}")
        return total


def run_test():
    """
    Test function for OldPatch class:
    - Detects existing Old Patch path
    - Opens selection/download window
    """
    root = ctk.CTk()
    root.geometry("400x200")
    root.title("Old Patch Test")

    old_patch = OldPatch()

    def test_detection():
        """
        Tests automatic detection of Old Patch path.
        """
        detected_path = old_patch.path
        result_label.configure(text=f"Detected Path:\n{detected_path if detected_path else 'None'}")

    def test_manual_or_download():
        """
        Opens the UI for manual selection or Steam download.
        """
        old_patch.get_old_patch(root)
        result_label.configure(text=f"Final Path:\n{old_patch.path if old_patch.path else 'None'}")

    ctk.CTkLabel(root, text="Old Patch Test Suite", font=("Arial", 16)).pack(pady=10)

    detect_button = ctk.CTkButton(root, text="🔍 Test Auto-Detection", command=test_detection)
    detect_button.pack(pady=5)

    download_button = ctk.CTkButton(root, text="📥 Test Selection/Download", command=test_manual_or_download)
    download_button.pack(pady=5)

    result_label = ctk.CTkLabel(root, text="Result will be displayed here", font=("Arial", 12))
    result_label.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_test()