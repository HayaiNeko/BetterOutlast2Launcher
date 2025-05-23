import os
import shutil
import customtkinter as ctk
from ui import fonts, colors
from settings import Setting
from widgets import CustomCheckboxes, Tooltip, TooltipPlaceholder
from typing import List, Tuple


class Mod:
    def __init__(self, name: str, paths: Tuple[str, str] = None, *settings: Setting):
        """
        :param name: Name of the Mod, used for identification and in the UI
        :param paths: Tuple containing the path for the base directory and the installation directory.
        Can be set to None if the mod only relies on settings.
        :param settings: Used for mods that needs to toggle settings during the installation
        """
        self.name = name
        self.paths: List[Tuple[str, str]] = []
        self.settings = settings
        self.base_directory = None

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
        """Install all files from the base directory into the installation directory. Enables all settings"""
        # Check if there are files to be installed
        if self.base_directory is not None:
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
        """Check all the files from the mod are present and if all settings are enabled"""
        # The mod is considered installed if all destination files exist.
        if all(os.path.exists(destination) for _, destination in self.paths):
            for setting in self.settings:
                if not setting.is_enabled():
                    return False
            return True
        return False

    def toggle(self):
        """Toggles the mod on and off"""
        if self.is_installed():
            self.uninstall()
        else:
            self.install()


class DisplayMod(Mod):
    # All DisplayMod instances
    display_mods = []

    def __init__(self, name, paths, tooltip_text: str = ""):
        super().__init__(name, paths)
        self.tooltip_text = tooltip_text

        self.__class__.display_mods.append(self)

    def newline(self, parent):
        """Create the UI line used to install and uninstall the mod"""
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.container.pack(fill="x", pady=10, padx=20)

        self.mod_label = ctk.CTkLabel(self.container, text=self.name, text_color=colors["text"], font=fonts["text"])
        self.mod_label.pack(side="left")

        self.status_label = ctk.CTkLabel(self.container, font=fonts["small"])
        self.action_button = ctk.CTkButton(self.container, text_color=colors["text"], font=fonts["small"], width=100,
                                           fg_color=colors["primary"], hover_color=colors["primary hover"],
                                           command=lambda: [self.toggle(), self.refresh_window()])
        if self.tooltip_text:
            self.tooltip = Tooltip(self.container, text=self.tooltip_text, shade=1)
        else:
            self.tooltip = TooltipPlaceholder(self.container)

        self.tooltip.pack(side="right", padx=10)
        self.action_button.pack(side="right", padx=10)
        self.status_label.pack(side="right", padx=10)

        self.refresh_window()

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
    sprint_delay = None

    def __init__(self, name, paths, *settings):
        super().__init__(name, paths, *settings)
        self.__class__.lw_mods.append(self)

    @classmethod
    def create_mod_selector(cls, master):
        cls.selector = CustomCheckboxes(master, "Mods", [(mod.name, None) for mod in cls.lw_mods],
                                        tooltip_text="Launch with the following modifcations:\n"
                                                     "- No CPK disables checkpoint killing.\n"
                                                     "- Cutscene Skip allows you to skip cutscene with an S+Q.\n"
                                                     "- No Stamina disables stamina, and sprint delay unless No CPK is selected.\n"
                                                     "(This is because modifying Sprint Delay is not allowed in No CPK No Stamina)")
        cls.selector.pack(pady=10, padx=10)

    @classmethod
    def disable_mods(cls):
        cls.selector.selected_values = set()
        for button in cls.selector.buttons:
            button.configure(fg_color=colors["background_shade2"])
            button.configure(state="disabled")

    @classmethod
    def enable_all(cls):
        for button in cls.selector.buttons:
            button.configure(state="normal")

    @classmethod
    def prepare_launch(cls):
        selected_mods = cls.selector.get_selected()
        for mod in cls.lw_mods:
            if not mod.name in selected_mods:
                mod.uninstall()
        for mod in cls.lw_mods:
            if mod.name in selected_mods:
                mod.install()

        if "No CPK" in selected_mods:
            cls.sprint_delay.enable()


