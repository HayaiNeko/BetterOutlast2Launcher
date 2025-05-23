import os
import time
import subprocess
import threading
import configparser
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui import fonts, colors
from widgets import show_error
from files import File
from settings import Setting

# Default Steam content folder path and IDs
APP_ID = "414700"       # Outlast 2
DEPOT_ID = "414701"     # Windows files depot
MANIFEST_ID = "7085410466650398118"  # Manifest from 10 May 2017
STEAM_CONTENT_PATH = rf"C:\Program Files (x86)\Steam\steamapps\content\app_{APP_ID}\depot_{DEPOT_ID}"


class OldPatch:
    CONFIG_SECTION = "OldPatch"

    def __init__(self):
        # Open the config file
        self.config_file = "LauncherConfig.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not self.config.has_section(OldPatch.CONFIG_SECTION):
            self.config.add_section(OldPatch.CONFIG_SECTION)

        # Load the saved path (default is empty)
        self.path = self.config.get(OldPatch.CONFIG_SECTION, "Path", fallback="")
        if not self.path:
            self.detect_path()

    def save_path(self):
        self.config.set(OldPatch.CONFIG_SECTION, "Path", self.path)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        print(f"Old Patch path saved: {self.path}")

    @staticmethod
    def is_valid_old_patch(path):
        """Checks if the provided path is structured like an OL2 folder."""
        if path and os.path.isdir(path):
            bat_file_path = os.path.join(path, "Outlast2.bat")
            if not os.path.isfile(bat_file_path):
                return False
            required_dirs = ["OLGame", "BInaries", "Engine"]
            for directory in required_dirs:
                if not os.path.isdir(os.path.join(path, directory)):
                    return False
            return True
        return False

    def detect_path(self):
        """Detects the old patch path in the default downloading spot"""
        # Supposons que le répertoire courant est "steamapps/common/Outlast 2"
        steamapps_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
        patch_path = os.path.join(steamapps_dir, "content", f"app_{APP_ID}", f"depot_{DEPOT_ID}")

        self.path = patch_path if self.is_valid_old_patch(patch_path) else ""
        self.save_path()

    def install_manage(self):
        """Open a Toplevel window for selecting or downloading the Old Patch."""
        self.window = ctk.CTkToplevel(fg_color=colors["background"])
        self.window.title("Old Patch Management")
        self.window.attributes("-topmost", True)
        self.window.geometry("600x400")  # Enlarged window

        # Title and current path display
        title = ctk.CTkLabel(self.window, text="Select your Old Patch Folder",
                              font=fonts["h3"], text_color=colors["text"])
        title.pack(pady=10)

        current_path_text = self.path if self.path else "No path defined"
        self.current_path_label = ctk.CTkLabel(self.window, text=current_path_text,
                                              font=fonts["text"], text_color=colors["text"])
        self.current_path_label.pack(pady=5)

        btn_select = ctk.CTkButton(
            self.window,
            text="📂 Select Folder",
            command=lambda: self.select_folder(self.window),
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        btn_select.pack(pady=5)

        # Download section
        label_steam = ctk.CTkLabel(self.window, text="Or download via Steam:",
                                   font=fonts["h3"], text_color=colors["text"])
        label_steam.pack(pady=(20, 10))

        btn_steam = ctk.CTkButton(
            self.window,
            text="🎮 Open Steam Console",
            command=self.open_steam_console,
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        btn_steam.pack(pady=5)

        self.copy_steam_command_button = ctk.CTkButton(
            self.window,
            text="📋 Copy Steam Download Command",
            command=self.copy_steam_command,
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        self.copy_steam_command_button.pack(pady=5)

        self.progress_label = ctk.CTkLabel(self.window, text="📥 Progress: 0.00%",
                                           font=fonts["small"], text_color=colors["text"])
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.window, progress_color=colors["primary"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        self.window.update_idletasks()
        threading.Thread(target=self.track_download, daemon=True).start()

    def select_folder(self, master):
        folder_selected = filedialog.askdirectory(title="Select Old Patch Folder", parent=master)
        if folder_selected:
            if not self.is_valid_old_patch(folder_selected):
                show_error("The selected folder is not a valid Old Patch folder.")
            else:
                self.path = folder_selected
                self.save_path()
                self.current_path_label.configure(text=self.path)

    def open_steam_console(self):
        subprocess.run("start steam://open/console", shell=True)

    def copy_steam_command(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(f"download_depot {APP_ID} {DEPOT_ID} {MANIFEST_ID}")
        self.window.update()
        self.copy_steam_command_button.configure(text="✅ Command Copied")

    def track_download(self):
        expected_size = 27096937514  # Expected size in bytes
        expected_size_gb = expected_size / (1024 ** 3)
        while not os.path.exists(STEAM_CONTENT_PATH):
            self.progress_label.configure(text="📥 Waiting for download to start...", text_color="orange")
            time.sleep(1)
        try:
            while True:
                total_size = self.get_folder_size(STEAM_CONTENT_PATH)
                progress = min(100.0, (total_size / expected_size) * 100)
                self.progress_label.configure(
                    text=f"📥 Progress: {progress:.2f}% ({total_size / (1024 ** 3):.2f} GB / {expected_size_gb:.2f} GB)",
                    text_color=colors["text"]
                )
                self.progress_bar.set(progress / 100)
                if total_size >= expected_size:
                    if not self.path:
                        self.progress_label.configure(text="✅ Download complete!", text_color="green")
                        self.path = STEAM_CONTENT_PATH
                        self.save_path()
                        break
                time.sleep(1)
        except Exception as e:
            print(e)

    @staticmethod
    def get_folder_size(path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except Exception as e:
                    print(f"Error on {fp}: {e}")
        return total

    def create_button(self, parent):
        """
        Create and return a CTkButton for managing/installing the Old Patch.
        """
        button = ctk.CTkButton(
            parent,
            text="Manage/Install Old Patch",
            command=lambda: self.install_manage(),
            font=fonts["h4"],
            text_color=colors["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"]
        )
        button.pack(padx=10, pady=20)

    def launch_old_patch(self):
        """
        Checks if the current Old Patch folder is non-empty and valid.
        If valid, triggers the launch procedure by executing the Outlast2.bat file.
        """
        if self.path and self.is_valid_old_patch(self.path):
            File.demo_directory = self.path
            File.sync_all_with_old_patch()
            demo_steam = Setting(name="Demo Steam",
                                 file=File(os.path.join(self.path, "OLGame", "Config", "DefaultEngine.ini"), demo_file=True),
                                 setting="bRelaunchInSteam=")
            demo_steam.disable()

            try:
                # Launch the batch file
                subprocess.Popen(os.path.join(self.path, "Binaries", "Win64", "Outlast2.exe"))
                print("Old Patch launched successfully.")
            except Exception as e:
                show_error(f"Error launching Old Patch:{e}")
        else:
            self.install_manage()

