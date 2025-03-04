import customtkinter as ctk
from ui import colors, fonts

class CustomRadioButtons(ctk.CTkFrame):
    def __init__(self, master, title, values, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        title = ctk.CTkLabel(self, text=title, text_color=colors["text"], font=fonts["h3"])
        title.pack(pady=5)
        self.buttons = []

        for index, (value, command) in enumerate(values):
            btn = ctk.CTkButton(
                self, text=value,
                width=120, height=32,
                font=fonts["h5"],
                text_color=colors["button text"],
                fg_color=colors["background_shade2"],
                hover_color=colors["primary hover"],
                command=lambda opt=value, cmd=command: self.select_option(opt, cmd)
            )
            btn.pack(pady=5, padx=5, side='left')
            self.buttons.append(btn)

        self.select_option(values[0][0], values[0][1])

    def select_option(self, value, command=None):
        self.selected_value = value

        for btn in self.buttons:
            if btn.cget("text") == value:
                btn.configure(fg_color=colors["primary"])
            else:
                btn.configure(fg_color=colors["background_shade2"])

        if command:
            command()

    def get_selected(self):
        return self.selected_value


class ModSelector(CustomRadioButtons):
    def __init__(self, master, title, values, **kwargs):
        super().__init__(master, title, values, **kwargs)
        self.disabled = False

    def disable_mods(self):
        for btn in self.buttons:
            self.select_option("Vanilla")
            if not (btn.cget("text") == "Vanilla"):
                btn.configure(state="disabled")
        self.disabled = True

    def enable_all(self):
        for btn in self.buttons:
            btn.configure(state="normal")
        self.disabled = False

