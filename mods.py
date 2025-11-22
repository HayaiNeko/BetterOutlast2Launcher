import os
import shutil
import customtkinter as ctk
from ui import fonts, colors
from settings import Setting
from widgets import CustomCheckboxes, InfoIcon, InfoIconPlaceholder
import hashlib


class Mod:
    """
    Represents a mod with optional source and install paths. Settings can be tied to the mod.
    This class manages installation. Child classes manage GUI and additional logic.
    """

    def __init__(self, name: str, source_path: str, install_path: str, *settings: Setting):
        self.name = name
        self.source_path = source_path      # Folder containing mod files (optional)
        self.install_path = install_path    # Destination folder in game (optional)
        self.settings = settings

    # --- Internal utils ---

    def _iter_source_files(self):
        """Yield (relative_path, absolute_source_path) for each file in the source directory."""
        if not self.source_path or not os.path.isdir(self.source_path):
            return  # silently skip if no source
        for root, _, files in os.walk(self.source_path):
            for file in files:
                abs_src = os.path.join(root, file)
                rel_path = os.path.relpath(abs_src, self.source_path)
                yield rel_path.replace("\\", "/"), abs_src

    # --- Core operations ---

    def install(self):
        """Install all files from source_path to install_path and enable settings."""
        print(f"[INFO] Installing mod '{self.name}'...")

        # Copy files only if paths are defined
        if self.source_path and self.install_path:
            if not os.path.isdir(self.source_path):
                print(f"[WARN] Source directory '{self.source_path}' not found.")
            else:
                for rel_path, src in self._iter_source_files():
                    dst = os.path.join(self.install_path, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    try:
                        shutil.copy2(src, dst)
                        print(f"[INFO] Copied '{rel_path}'")
                    except Exception as e:
                        print(f"[ERROR] Could not copy '{src}': {e}")

        # Enable all related settings
        for s in self.settings:
            s.enable()

    def uninstall(self):
        """Remove files corresponding to the source and disable settings."""
        print(f"[INFO] Uninstalling mod '{self.name}'...")

        # Remove only matching files if paths exist
        if self.source_path and self.install_path:
            if not os.path.isdir(self.source_path):
                print(f"[WARN] Source directory '{self.source_path}' not found.")
            else:
                for rel_path, _ in self._iter_source_files():
                    dst = os.path.join(self.install_path, rel_path)
                    if os.path.exists(dst):
                        try:
                            os.remove(dst)
                            print(f"[INFO] Removed '{rel_path}'")
                        except Exception as e:
                            print(f"[ERROR] Could not remove '{dst}': {e}")
                    else:
                        print(f"[WARN] File not found: '{rel_path}'")

        # Disable all related settings
        for s in self.settings:
            s.disable()

    def is_installed(self) -> bool:
        """Return True if all source files exist in the install directory and all settings are enabled."""
        if self.source_path and self.install_path:
            if os.path.isdir(self.source_path):
                for rel_path, _ in self._iter_source_files():
                    dst = os.path.join(self.install_path, rel_path)
                    if not os.path.exists(dst):
                        return False

        # Check all settings are enabled
        for s in self.settings:
            if not s.is_enabled():
                return False

        return True

    def toggle(self):
        """Toggle the mod on/off depending on installation state."""
        if self.is_installed():
            self.uninstall()
        else:
            self.install()




class DisplayMod(Mod):
    # All DisplayMod instances
    display_mods = []

    def __init__(self, name, source_path, install_path, tooltip_text: str = ""):
        super().__init__(name, source_path, install_path)
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
            self.tooltip = InfoIcon(self.container, text=self.tooltip_text, shade=1)
        else:
            self.tooltip = InfoIconPlaceholder(self.container)

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

    def __init__(self, name, source_path, install_path, *settings):
        super().__init__(name, source_path, install_path, *settings)
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


class ReplacementMod:
    """Mod that works by replacing an existing files. The original copy of the files needs to be provided."""

    def __init__(self, name: str, mod_source_path: str, original_source_path: str, install_path: str, *settings):
        self.mod_source = Mod(f"modded_{name}", mod_source_path, install_path)
        self.original_source = Mod(f"original_{name}", original_source_path, install_path)

        self.name = name
        self.settings = settings

    @staticmethod
    def _calculate_file_hash(filepath: str) -> str:
        """Calculates the SHA256 hash of a file for content verification."""
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return ""

        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as file:
                buf = file.read(65536)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(65536)
            return hasher.hexdigest()
        except Exception:
            print(f"[Error] Couldn't calculate the hash of {filepath}")

    def install(self):
        """Copies modded files and enables settings."""
        print(f"[INFO] Installing replacement mod '{self.name}'...")
        self.mod_source.install()
        for s in self.settings:
            s.enable()

    def uninstall(self):
        """Restores original files and disables settings."""
        print(f"[INFO] Uninstalling replacement mod '{self.name}'...")
        self.original_source.install()
        for s in self.settings:
            s.disable()

    def is_installed(self) -> bool:
        """
        Returns True if the installed file matches the MODDED file (verified via hash)
        AND if all settings are enabled.
        """

        if self.mod_source.source_path and self.mod_source.install_path:

            for rel_path, src_mod_path in self.mod_source._iter_source_files():
                dst_installed_path = os.path.join(self.mod_source.install_path, rel_path)

                if not os.path.exists(dst_installed_path):
                    return False

                hash_source = self._calculate_file_hash(src_mod_path)
                hash_installed = self._calculate_file_hash(dst_installed_path)

                # Check for hash match
                if not hash_source or hash_source != hash_installed:
                    return False

        for s in self.settings:
            if not s.is_enabled():
                return False

        return True
