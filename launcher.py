import customtkinter as ctk
from launcher_settings import LauncherSettings
from old_patch import OldPatch
from mods import Mod, LWMod, DisplayMod
from bindings import Binding
from settings import DisplaySetting
import subprocess
from widgets import CustomRadioButtons, CustomTopLevel, show_error
from ui import colors, fonts
from paths import *
import tkinter as tk


class Launcher:
    def __init__(self, current_version):
        self.root = ctk.CTk(fg_color=colors["background"])
        self.root.geometry("600x600")
        self.root.title("Better Outlast II Launcher")

        self.root.iconphoto(True, tk.PhotoImage(file=OL2_ICON))

        self.main_content = ctk.CTkFrame(self.root, fg_color=colors["background_shade1"])
        self.main_content.pack(fill="x", padx=20, pady=20)

        self.title = ctk.CTkLabel(
            self.main_content,
            text="Better Outlast II Launcher",
            text_color=colors["text"],
            font=fonts["h1"]
        )
        self.title.pack(pady=20)

        self.launcher_settings = LauncherSettings()
        self.old_patch = OldPatch()
        self.version = current_version

        self.mod_loader = Mod("ModLoader",
                              (os.path.join(GAME_DIRECTORY, "Mods", "ModLoader"),
                               os.path.join(GAME_DIRECTORY, "Binaries", "Win64")))

        self.create_radio_buttons()
        self.create_launch_button()
        self.create_config_buttons()
        self.create_footer()

    def create_radio_buttons(self):
        self.patch_selector = CustomRadioButtons(
            self.main_content,
            title="Patch",
            values=[("Latest Patch", LWMod.enable_all), ("Old Patch", LWMod.disable_mods)]
        )
        self.patch_selector.pack(pady=10)

        LWMod.create_mod_selector(self.main_content)

    def create_launch_button(self):
        self.launch_button = ctk.CTkButton(
            self.main_content,
            text="Launch Game",
            width=250,
            height=60,
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["button text"],
            font=fonts["h2"],
            command=self.launch_game
        )
        self.launch_button.pack(pady=30)

    def create_config_buttons(self):
        self.config_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.config_frame.pack(pady=10)

        self.bindings_button = ctk.CTkButton(
            self.config_frame,
            text="Configure Bindings",
            width=200,
            height=40,
            text_color=colors["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            font=fonts["h4"],
            command=self.open_bindings_window
        )
        self.bindings_button.grid(row=0, column=0, padx=10)

        self.settings_button = ctk.CTkButton(
            self.config_frame,
            text="Option and Mods",
            width=200,
            height=40,
            text_color=colors["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            font=fonts["h4"],
            command=self.open_settings_window
        )
        self.settings_button.grid(row=0, column=1, padx=10)

    def create_footer(self):
        # Version
        version_label = ctk.CTkLabel(self.root, text=f"Launcher Version : {self.version}", font=fonts["small"])
        version_label.pack(side="bottom", pady=5)

        # Credits
        credits_title = ctk.CTkLabel(self.root, text="Credits", font=fonts["h5"])
        credits_label = ctk.CTkLabel(self.root, text="Launcher made by HayaiNeko.\n"
                                                "Thanks to lanylow for developing the mods.",
                                     font=fonts["small"])
        credits_label.pack(side="bottom", pady=(0, 5))
        credits_title.pack(side="bottom", pady=0)

    def lift_launcher(self):
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.root.after(100, lambda: self.root.attributes("-topmost", False))

    def open_bindings_window(self):
        if Binding.window is None:
            Binding.window = CustomTopLevel(self.root, "Configure Bindings", 560, 600)
            Binding.lift_launcher = self.lift_launcher
            Binding.show_window()

    def open_settings_window(self):
        settings_window = CustomTopLevel(self.root, "Option and Mods", 560, 666)

        def delete_window():
            settings_window.destroy()
            self.lift_launcher()

        settings_window.protocol("WM_DELETE_WINDOW", delete_window)

        DisplayMod.show_mods(window=settings_window)
        DisplaySetting.show_settings(window=settings_window)
        self.launcher_settings.display(settings_window)
        self.old_patch.create_button(settings_window)

    def launch_game(self):
        patch = self.patch_selector.selected_value
        LWMod.prepare_launch()
        if patch == "Latest Patch":
            self.mod_loader.install()
            try:
                # Launch the batch file
                subprocess.Popen(os.path.join(GAME_DIRECTORY, "Binaries", "Win64", "Outlast2.exe"), shell=True)
                print("Launching Outlast II...")
            except Exception as e:
                show_error(f"Error launching Outlast II: {e}")
        elif patch == "Old Patch":
            self.old_patch.launch_old_patch()

        if self.launcher_settings.close_on_launch:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

