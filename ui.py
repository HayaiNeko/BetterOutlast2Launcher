import tkinter

import customtkinter as ctk
from PIL import Image, ImageTk

fonts = {
    "text": ("Inter", 14),
    "small": ("Inter", 12),
    "h1": ("Inter", 32, "bold"),
    "h2": ("Inter", 24, "bold"),
    "h3": ("Inter", 20, "bold"),
    "h4": ("Inter", 16, "bold"),
    "h5": ("Inter", 14, "bold"),
}

colors = {
    "text": "#ffffff",
    "button text": "#ffffff",
    "background": "#1a1a1a",
    "background_shade1": "#262626",
    "background_shade2": "#333333",
    "background_shade3": "#404040",
    "primary": "#055749",
    "primary hover": "#04483d",
    "secondary": "#01322B",
    "accent": "#088c78",
    "success": "green",
    "error": "red"
}


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


if __name__ == "__main__":
    # Création de la fenêtre principale
    root = ctk.CTk()
    root.geometry("600x600")
    root.title("Test CustomRadioButtons")

    # Charger une image PNG comme icône
    icon = tkinter.PhotoImage(file="OutlastII_icon.png")


    # Appliquer l'icône
    root.iconphoto(True, icon)

    main_content = ctk.CTkFrame(root,fg_color=colors["background_shade1"])
    main_content.pack(pady=20)

    title = ctk.CTkLabel(main_content, text="Better Outlast II Launcher", text_color=colors["text"], font=fonts["h1"])
    title.pack(pady=20)

    # Création et affichage du groupe de boutons radio
    patch_selector = CustomRadioButtons(main_content, title="Patch", values=[("Latest Patch", None), ("Old Patch", lambda:print("OLD PATCH YEP"))])
    patch_selector.pack(pady=10, padx=10)

    mods_selector = CustomRadioButtons(main_content, title="Mod",
                                            values=[("Vanilla", None), ("No CPK", None), ("Cutscene Skip", None),
                                                    ("No Stamina", None)])
    mods_selector.pack(pady=10, padx=10)



    launch_button = ctk.CTkButton(main_content, text="Launch Game", width=250, height=60,
                                fg_color=colors["primary"], hover_color=colors["primary hover"], text_color=colors["button text"], font=fonts["h2"],
                                command= lambda: print(f"Selected Patch: {patch_selector.get_selected()} \nSelected Mod: {mods_selector.get_selected()}"))
    launch_button.pack(pady=30)

    config_frame = ctk.CTkFrame(root, fg_color="transparent")
    config_frame.pack(pady=10)

    bindings_button = ctk.CTkButton(config_frame, text="Configure Bindings", width=200, height=40,
                                    text_color=colors["button text"], fg_color=colors["primary"], hover_color=colors["primary hover"], font=fonts["h4"],
                                    command=lambda: print('open bindings page'))
    bindings_button.grid(row=0, column=0, padx=10)

    mods_button = ctk.CTkButton(config_frame, text="Option and Mods", width=200, height=40,
                                    text_color=colors["button text"], fg_color=colors["primary"],
                                    hover_color=colors["primary hover"], font=fonts["h4"],
                                    command=lambda: print('open mods page'))
    mods_button.grid(row=0, column=1, padx=10)

    # Lancement de la boucle principale de l'interface graphique
    root.mainloop()