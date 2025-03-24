import customtkinter as ctk
from typing import List, Tuple
from ui import colors, fonts
import tkinter as tk
from tkinter import messagebox


def show_error(message):
    """Display a messagebox for errors"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message, parent=root)
    root.destroy()


class CustomTopLevel(ctk.CTkToplevel):
    def __init__(self, parent, title: str, width: int, height: int):
        super().__init__(parent ,fg_color=colors["background"])
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        self.after(100, lambda: self.attributes("-topmost", False))


class CustomRadioButtons(ctk.CTkFrame):
    def __init__(self, master, title: str, values):
        super().__init__(master, fg_color="transparent")

        title = ctk.CTkLabel(self, text=title, text_color=colors["text"], font=fonts["h3"])
        title.pack(pady=5)
        self.buttons = []

        for index, (value, command) in enumerate(values):
            button = ctk.CTkButton(
                self, text=value,
                width=120, height=32,
                font=fonts["h5"],
                text_color=colors["button text"],
                fg_color=colors["background_shade2"],
                hover_color=colors["primary hover"],
                command=lambda opt=value, cmd=command: self.select_option(opt, cmd)
            )
            button.pack(pady=5, padx=5, side='left')
            self.buttons.append(button)

        self.select_option(values[0][0])

    def select_option(self, value, command=None):
        self.selected_value = value

        for button in self.buttons:
            if button.cget("text") == value:
                button.configure(fg_color=colors["primary"])
            else:
                button.configure(fg_color=colors["background_shade2"])

        if command:
            command()

    def get_selected(self):
        return self.selected_value


class CustomCheckboxes(ctk.CTkFrame):
    def __init__(self, master, title: str, values):
        """
        :param master: widget parent
        :param title: title of the checkbox section
        :param values: (value, command). Command is executed on button press
        """
        super().__init__(master, fg_color="transparent")

        # Label de titre
        title_label = ctk.CTkLabel(
            self, text=title,
            text_color=colors["text"],
            font=fonts["h3"]
        )
        title_label.pack(pady=5)

        self.buttons = []           # Pour stocker les références des boutons
        self.selected_values = set()  # Contiendra les valeurs sélectionnées

        # Création d'un bouton pour chaque valeur
        for (value, command) in values:
            button = ctk.CTkButton(
                self,
                text=value,
                width=120,
                height=32,
                font=fonts["h5"],
                text_color=colors["button text"],
                fg_color=colors["background_shade2"],
                hover_color=colors["primary hover"],
                command=lambda val=value, cmd=command: self.toggle_option(val, cmd)
            )
            button.pack(pady=5, padx=5, side='left')
            self.buttons.append(button)

    def toggle_option(self, value, command=None):
        """
        Coche ou décoche l'option `value`.
        Modifie aussi la couleur du bouton concerné.
        """
        # Trouver le bouton correspondant
        for button in self.buttons:
            if button.cget("text") == value:
                # Si la valeur est déjà sélectionnée, on la retire
                if value in self.selected_values:
                    self.selected_values.remove(value)
                    button.configure(fg_color=colors["background_shade2"])
                else:
                    # Sinon on ajoute la valeur à l'ensemble
                    self.selected_values.add(value)
                    button.configure(fg_color=colors["primary"])
                break

        # Appeler la fonction associée si elle existe
        if command:
            command()

    def get_selected(self):
        """
        Retourne la liste (ou l'ensemble) des valeurs sélectionnées.
        """
        return self.selected_values


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
        self.circle = self.canvas.create_oval(2, 2, 22, 22, fill=colors["primary"], outline=colors["secondary"])

        # Ajout du point d'interrogation centré
        self.canvas.create_text(12, 12, text="?", font=fonts["small"], fill="white", anchor="center")

        # hover events
        self.canvas.bind("<Enter>", self.show_tooltip)
        self.canvas.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window is None:
            bg_color = colors[f"background_shade{self.shade+1}"]
            self.tooltip_window = ctk.CTkToplevel(self.winfo_toplevel())
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.attributes("-topmost", True)
            self.tooltip_window.lift()


            label = ctk.CTkLabel(self.tooltip_window, text=self.text,
                                 text_color=colors["button text"],
                                 fg_color=bg_color,
                                 corner_radius=10,
                                 font=fonts["text"], padx=2, pady=5)
            label.pack()

        self.tooltip_window.geometry(f"+{self.winfo_rootx() + 30}+{self.winfo_rooty() - 10}")

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class DeleteButton(ctk.CTkButton):
    def __init__(self, parent, background_color, command=None, **kwargs):
        self.background_color = background_color
        super().__init__(
            parent,
            text="✕",
            width=25,
            fg_color="transparent",
            text_color=background_color,
            hover_color=background_color,
            command=command,
            corner_radius=50,
            **kwargs
        )
        self.normal_text_color = colors["text"]
        self.hover_text_color = "#A0A0A0"
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(text_color=self.hover_text_color)

    def on_leave(self, event):
        self.configure(text_color=self.background_color)


class DeletePlaceHolder(ctk.CTkButton):
    def __init__(self, parent, background_color):
        super().__init__(
            parent,
            text="✕",
            width=25,
            fg_color="transparent",
            text_color=background_color,
            hover_color=background_color,
            corner_radius=50,
        )


