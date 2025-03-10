import os
import shutil
import customtkinter as ctk
from utils import show_error
from ui import fonts, colors
from settings import Setting
from widgets import ModSelector
from files import File
from typing import List, Tuple


class Mod:
    def __init__(self, name: str, paths: Tuple[str, str] = None, *settings: Setting):
        """
        :param name: Name of the Mod, used for identification and in the UI
        :param paths: Tuple containing the path for the base directory and the installation directory
        :param settings: Used for mods that needs to toggle settings during the installation
        """
        self.name = name
        self.paths: List[Tuple[str, str]] = []
        self.settings = settings

        if paths is not None:
            self.base_directory = paths[0]
            self.install_directory = paths[1]

            # Get all file paths from the base directory
            if os.path.exists(self.base_directory):
                for item in os.listdir(self.base_directory):
                    source = os.path.join(self.base_directory, item)
                    destination = os.path.join(self.install_directory, item)
                    self.paths.append((source, destination))
            else:
                print(f"[ERROR] Base directory '{self.base_directory}' doesn't exist.")

    def install(self):
        """Install all of the files from the base directory into the installation directory. Enables all settings"""
        # Ensure the installation directory exists
        if not os.path.exists(self.install_directory):
            os.makedirs(self.install_directory)

        # Copy each file or directory from source to destination
        for source, destination in self.paths:
            if os.path.exists(source):
                try:
                    if os.path.isdir(source):
                        shutil.copytree(source, destination, dirs_exist_ok=True)
                        print(f"[INFO] Copied directory '{source}' to '{destination}'.")
                    else:
                        shutil.copy(source, destination)
                        print(f"[INFO] Copied file '{source}' to '{destination}'.")
                except Exception as e:
                    print(f"[ERROR] Error copying '{source}' to '{destination}': {e}")
            else:
                print(f"[ERROR] Source path '{source}' does not exist. Skipping.")

        # Enable all settings
        for setting in self.settings:
            setting.enable()

    def uninstall(self):
        """Uninstall all the files from the mod. Disables all settings"""
        # Remove each destination file
        for _, destination in self.paths:
            if os.path.exists(destination):
                try:
                    os.remove(destination)
                    print(f"[INFO] Removed '{destination}'.")
                except Exception as e:
                    print(f"[ERROR] Could not remove '{destination}': {e}")
            else:
                print(f"[ERROR] Destination file '{destination}' does not exist.")

        # Disable all settings
        for setting in self.settings:
            setting.disable()

    def is_installed(self) -> bool:
        """Check all the files from the mod are present"""
        # The mod is considered installed if all destination files exist.
        return all(os.path.exists(destination) for _, destination in self.paths)

    def toggle(self):
        """Toggles the mod on and off"""
        if self.is_installed():
            self.uninstall()
        else:
            self.install()


class DisplayMod(Mod):
    # All DisplayMod instances
    display_mods = []

    def __init__(self, name, paths, *settings):
        super().__init__(name, paths, *settings)
        self.__class__.display_mods.append(self)

        # UI Elements
        self.container = None
        self.mod_label = None
        self.status_label = None
        self.action_button = None

    def newline(self, parent):
        """Create the UI line used to install and uninstall the mod"""
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.container.pack(fill="x", pady=10, padx=20)

        self.mod_label = ctk.CTkLabel(self.container, text=self.name, text_color=colors["text"], font=fonts["text"])

        if self.is_installed():
            status_text, status_color = "Installed", colors["success"]
            action_text = "Uninstall"
        else:
            status_text, status_color = "Not Installed", colors["error"]
            action_text = "Install"

        self.status_label = ctk.CTkLabel(self.container, text=status_text, text_color=status_color, font=fonts["small"])
        self.action_button = ctk.CTkButton(self.container, text=action_text, text_color=colors["text"],
                                           font=fonts["small"], width=100,
                                           command=lambda: [self.toggle(), self.refresh_window()])

    def refresh_window(self):
        """Refreshes the UI when the mod is installed/uninstalled"""
        if self.is_installed():
            status_text, status_color = "Installed", colors["success"]
            action_text = "Uninstall"
        else:
            status_text, status_color = "Not Installed", colors["error"]
            action_text = "Install"
        self.status_label.configure(text=status_text, text_color=status_color)
        self.action_button.configure(text=action_text)

    @classmethod
    def show_mods(cls, window):
        """Shows all instances of DisplayMod in a dedicated frame"""
        frame = ctk.CTkFrame(window, fg_color=colors["background_shade1"])
        frame.pack(pady=10, fill="x", padx=20)

        title = ctk.CTkLabel(frame, text="Mods", text_color=colors["text"], font=fonts["h3"])
        title.pack(pady=10)

        for mod in cls.display_mods:
            mod.newline(frame)


class LWMod(Mod):
    lw_mods = []
    selector = None

    def __init__(self, name, paths, *settings):
        super().__init__(name), paths, *settings
        self.__class__.lw_mods.append(self)

    @classmethod
    def create_mod_selector(cls, master):
        cls.selector = ModSelector(master, "Mods", [(mod.name, None) for mod in cls.lw_mods])
        cls.selector.pack(pady=10, padx=10)

    @classmethod
    def prepare_launch(cls):
        selected_mods = cls.selector.get_selected()
        for mod in cls.lw_mods:
            if mod.name in selected_mods:
                mod.install()
            else:
                mod.uninstall()
