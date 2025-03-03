import os
import shutil
import customtkinter as ctk
from utils import show_error
from ui import fonts, colors
from settings import Setting


class Mod:
    def __init__(self, name: str, base_paths: list[str], install_paths: list[str]):
        assert len(base_paths) == len(install_paths), "base_paths and install paths have different lengths"

        for path in base_paths:
            assert os.path.exists(path), f"{path} does not exist"

        self.name = name
        self.install_paths = install_paths
        self.paths = zip(base_paths, install_paths)

    def install(self):
        for base_path, install_path in self.paths:
            try:
                if os.path.isfile(base_path):
                    if not os.path.exists(install_path):
                        os.makedirs(install_path)
                    shutil.copy(base_path, install_path)
                elif os.path.isdir(base_path):
                    shutil.copytree(base_path, install_path, dirs_exist_ok=True)
                print(f"{base_path} successfully moved to {install_path}")

            except Exception as e:
                show_error(f"Couldn't install {base_path} to {install_path}: {e}")

    def uninstall(self):
        for install_path in self.install_paths:
            if os.path.exists(install_path):
                try:
                    if os.path.isfile(install_path):
                        os.remove(install_path)
                    elif os.path.isdir(install_path):
                        shutil.rmtree(install_path)
                    print(f"{install_path} uninstalled successfully")

                except Exception as e:
                    show_error(f"Couldn't uninstall {install_path}: {e}")

    def is_installed(self):
        for install_path in self.install_paths:
            if not os.path.exists(install_path):
                return False
        return True

    def toggle_install(self):
        if self.is_installed():
            self.uninstall()
        else:
            self.install()


class DllMod(Mod):
    dll_mods = []

    def __init__(self, name: str, base_paths: list[str], install_paths: list[str], mod_dependant_setting: Setting = None):
        super().__init__(name, base_paths, install_paths)

        self.mod_dependant_setting = mod_dependant_setting

        self.__class__.dll_mods.append(self)

    def uninstall(self):
        super().uninstall()
        if self.mod_dependant_setting is not None:
            self.mod_dependant_setting.enable()

    def newline(self, parent):
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
        self.action_button = ctk.CTkButton(self.container, text=action_text, text_color=colors["button text"],
                                           font=fonts["small"], width=100,
                                           command=lambda: [self.toggle_install(), self.refresh_window()])

    def refresh_window(self):
        if self.is_installed():
            status_text, status_color = "Installed", colors["success"]
            action_text = "Uninstall"
        else:
            status_text, status_color = "Not Installed", colors["error"]
            action_text = "Install"
        self.status_label.configure(text=status_text, text_color=status_color)
        self.action_button.configure(text=action_text)

        if self.mod_dependant_setting is not None:
            self.mod_dependant_setting.refresh_window()

    @classmethod
    def show_mods(cls, frame):
        title = ctk.CTkLabel(frame, text="Mods", text_color=colors["text"], font=fonts["h2"])
        title.pack(pady=10)
        for dll_mod in cls.dll_mods:
            dll_mod.newline(frame)


class LWMod(Mod):
    LWMods = []
    selected_mod = None

    def __init__(self, name:str, base_paths: list[str], install_paths: list[str]):
        super().__init__(name, base_paths, install_paths)
        self.launch_path = self.install_paths[0]

        self.__class__.LWMods.append(self)
        if self.name == "None":
            self.__class__.selected_mod = self

    def init_launch(self):
        self.install()
        self.launch()

    def launch(self):
        pass

    @classmethod
    def launch_selected_mod(cls):
        cls.selected_mod.init_launch()


class SuperJump(LWMod):
    def __init__(self, name:str, base_paths: list[str], install_paths: list[str], root: ctk.CTk):
        super().__init__(name, base_paths, install_paths)
        self.root = root

    def init_launch(self):
        self.show_superjump_window()

    def show_superjump_window(self):
        pass
