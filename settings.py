from utils import show_error
from ui import fonts, colors
import customtkinter as ctk
from files import File


class Setting:
    settings = []

    def __init__(self, name: str, file: File, setting: str,):
        assert setting[-1] == "=", "Setting format invalid"

        self.name = name
        self.file = file
        self.setting = setting

        self.__class__.settings.append(self)

    def toggle(self):
        i, line = self.file.get_line(self.setting)
        if i >= 0:
            current_value = line.split("=")[-1].strip().upper()
            new_value = "FALSE" if current_value  == "TRUE" else "TRUE"
            self.file.replace_index(f"{self.setting}{new_value}", i, line)
            self.file.write_lines()

    def is_enabled(self):
        i, line = self.file.get_line(self.setting)
        if i >= 0:
            return line.split("=")[-1].strip().upper() == "TRUE"
        show_error(f"Couldn't find {self.setting} in {self.file.path}")

    def enable(self):
        if not self.is_enabled():
            self.toggle()

    def newline(self, frame):
        self.container = ctk.CTkFrame(frame, fg_color="Transparent")
        self.container.pack(fill="x", pady=10, padx=20)

        self.setting_label = ctk.CTkLabel(self.container, text=self.name, text_color=colors["text"], font=fonts["text"])

        if self.is_enabled():
            status_text, status_color = "Enabled", colors["success"]
            action_text = "Disable"
        else:
            status_text, status_color = "Disabled", colors["error"]
            action_text = "Enable"

        self.status_label = ctk.CTkLabel(self.container, text=status_text, text_color=status_color, font=fonts["small"])
        self.action_button = ctk.CTkButton(self.container, text=action_text, text_color=colors["button text"], font=fonts["small"], width=100,
                                           command= lambda: [self.toggle(), self.refresh_window()])

        self.setting_label.pack(side="left")
        self.action_button.pack(side="right")
        self.status_label.pack(side="right")

    def refresh_window(self):
        if self.is_enabled():
            status_text, status_color = "Enabled", colors["success"]
            action_text = "Enable"
        else:
            status_text, status_color = "Disabled", colors["error"]
            action_text = "Enable"
        self.status_label.configure(text=status_text, text_color=status_color)
        self.action_button.configure(text=action_text)

    @classmethod
    def show_settings(cls, frame):
        title = ctk.CTkLabel(frame, text="Settings", text_color=colors["text"], font=fonts["h2"])
        title.pack(pady=10)
        for setting in cls.settings:
            setting.newline()