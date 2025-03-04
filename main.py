import tkinter
import paths
import customtkinter as ctk
from ui import colors, fonts
from widgets import CustomRadioButtons, ModSelector
from bindings import Binding
import tkinter as tk

class LauncherUI:
    def __init__(self):
        self.root = ctk.CTk(fg_color=colors["background"])
        self.root.geometry("600x600")
        self.root.title("Better Outlast II Launcher")


        self.root.iconphoto(True, tk.PhotoImage(file="OutlastII_icon.png"))

        self.main_content = ctk.CTkFrame(self.root, fg_color=colors["background_shade1"])
        self.main_content.pack(pady=20)

        self.title = ctk.CTkLabel(
            self.main_content,
            text="Better Outlast II Launcher",
            text_color=colors["text"],
            font=fonts["h1"]
        )
        self.title.pack(pady=20)

        self.create_radio_buttons()
        self.create_launch_button()
        self.create_config_buttons()

    def create_radio_buttons(self):
        self.mods_selector = ModSelector(
            self.main_content,
            title="Mod",
            values=[("Vanilla", None), ("No CPK", None), ("Cutscene Skip", None), ("No Stamina", None)]
        )

        self.patch_selector = CustomRadioButtons(
            self.main_content,
            title="Patch",
            values=[("Latest Patch", self.mods_selector.enable_all), ("Old Patch", self.mods_selector.disable_mods)]
        )

        self.patch_selector.pack(pady=10)
        self.mods_selector.pack(pady=10, padx=10)

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
            text_color=colors["button text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            font=fonts["h4"],
            command=self.open_bindings_window
        )
        self.bindings_button.grid(row=0, column=0, padx=10)

        self.mods_button = ctk.CTkButton(
            self.config_frame,
            text="Option and Mods",
            width=200,
            height=40,
            text_color=colors["button text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            font=fonts["h4"],
            command=lambda: print('open mods page')
        )
        self.mods_button.grid(row=0, column=1, padx=10)

    def lift_launcher(self):
        pass

    def open_bindings_window(self):
        bindings_window = ctk.CTkToplevel(self.root)
        Binding.show_bindings(window=bindings_window, lift_launcher=self.lift_launcher)


    def launch_game(self):
        print(f"Selected Patch: {self.patch_selector.get_selected()} \nSelected Mod: {self.mods_selector.get_selected()}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LauncherUI()
    app.run()
