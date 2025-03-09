import customtkinter as ctk
from ui import colors, fonts
import ctypes


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



class Tooltip(ctk.CTkFrame):
    def __init__(self, parent, text, shade=0, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.text = text
        self.shade = shade
        self.parent = parent
        self.tooltip_window = None

        # Création du Canvas pour dessiner le cercle
        self.canvas = ctk.CTkCanvas(self, width=24, height=24, highlightthickness=0,
                                    bg=colors[f"background_shade{self.shade}"])
        self.canvas.pack()

        # Dessin du cercle
        self.circle = self.canvas.create_oval(2, 2, 22, 22, fill=colors["primary"], outline="black")

        # Ajout du point d'interrogation centré
        self.canvas.create_text(12, 12, text="?", font=fonts["small"], fill="white", anchor="center")

        # hover events
        self.canvas.bind("<Enter>", self.show_tooltip)
        self.canvas.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window is None:
            bg_color = colors[f"background_shade{self.shade+1}"]
            self.tooltip_window = ctk.CTkToplevel(self.parent)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.attributes("-topmost", True)
            self.tooltip_window.attributes('-alpha', 0.9)


            label = ctk.CTkLabel(self.tooltip_window, text=self.text,
                                 text_color=colors["button text"],
                                 fg_color=bg_color,
                                 corner_radius=10,
                                 font=fonts["small"], padx=5, pady=2)
            label.pack()

        self.tooltip_window.geometry(f"+{self.winfo_rootx() + 30}+{self.winfo_rooty() - 10}")

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
