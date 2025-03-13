import customtkinter as ctk
from ui import fonts, colors
from files import File
from threading import Thread
from VKcode import get_keypress
from widgets import Tooltip


class Binding:
    file: File = None
    demo_file: File = None
    bindings = []
    other_bindings = []
    fps_bindings = []

    def __init__(self, command: str, description: str, tooltip: str = None):
        self.command = command
        self.description = description
        self.tooltip = tooltip
        self.key = ""
        self.disabled = False

        self.__class__.bindings.append(self)

        if "Set OLEngine MaxSmoothedFrameRate " in self.command:
            self.__class__.fps_bindings.append(self)
        else:
            self.__class__.other_bindings.append(self)

    def load_binding(self):
        _, line = self.file.get_line('.Bindings=(Name="', self.command)
        if line is not None:
            self.disabled = line.startswith(";-")
            self.key = line.split('"')[1]
            return
        self.disabled = False
        self.key = ""

    def save_binding(self):
        prefix = ";-" if self.disabled else ""
        newline = f'{prefix}.Bindings=(Name="{self.key}",Command="{self.command}")'
        self.file.replace_or_add(newline, ".Bindings=(", self.command)

    @classmethod
    def load_bindings(cls):
        for binding in cls.bindings:
            binding.load_binding()

    @classmethod
    def save_bindings(cls):
        for binding in cls.bindings:
            binding.save_binding()
        cls.file.write_lines()

    @classmethod
    def sync_with_demo(cls):
        if cls.file is None or cls.demo_file is None:
            print("[ERROR] One of the files is None")
            return
        cls.file.copy_file(cls.demo_file)

    def wait_for_keypress(self):
        key_name = get_keypress()
        if key_name:
            self.key = key_name
            self.button.configure(text=key_name)
        else:
            self.button.configure(text="Unrecognized")

    def change_binding(self):
        """Prompt the user to press a key to set the new binding."""
        self.button.configure(text=">...<")
        Thread(target=self.wait_for_keypress, daemon=True).start()

    def disable_binding(self):
        self.disabled = not self.disabled
        self.toggle.configure(text="Disabled" if self.disabled else "Enabled")

    def newline(self, parent, row):
        self.label = ctk.CTkLabel(parent, text=self.description, font=fonts["text"], text_color=colors["text"], width=150, anchor="w")
        self.button = ctk.CTkButton(parent, text=self.key, font=fonts["text"], text_color=colors["button text"],
                                    command=self.change_binding, fg_color=colors["primary"],
                                    hover_color=colors["primary hover"], width=150)
        self.toggle = ctk.CTkSwitch(parent, text="Disabled" if self.disabled else "Enabled", font=fonts["small"], text_color=colors["text"],
                                    progress_color= colors["primary"], width = 80, command=self.disable_binding)


        self.label.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        self.button.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.toggle.grid(row=row, column=2, padx=15, pady=5, sticky="ew")

        if self.tooltip:
            self.tooltip = Tooltip(parent, text=self.tooltip, shade=1)
            self.tooltip.grid(row=row, column=3, padx=10, pady=5, sticky="ew")

        if not self.disabled:
            self.toggle.select()
        else:
            self.toggle.deselect()

    @classmethod
    def show_bindings(cls, window, lift_launcher):
        window.title("Configure Bindings")
        window.attributes('-topmost', True)
        window_width = 560
        window_height = 100 + min(len(cls.bindings), 10) * 40
        window.geometry(f"{window_width}x{window_height}")

        title = ctk.CTkLabel(window, text="Configure Bindings", text_color=colors["text"], font=fonts["h2"])
        title.pack(pady=10)

        bindings_frame = ctk.CTkScrollableFrame(window, fg_color=colors["background_shade1"],
                                                scrollbar_button_hover_color=colors["secondary hover"],
                                                scrollbar_button_color=colors["secondary"])
        bindings_frame.pack(fill="both", expand=True, padx=10, pady=(20, 0))

        cls.load_bindings()

        # command bindings
        command_bindings_title = ctk.CTkLabel(bindings_frame, text = "Commands",
                                              text_color=colors["text"], font=fonts["h4"])
        command_bindings_title.pack(pady=(10, 5))

        other_bindings_frame = ctk.CTkFrame(bindings_frame, fg_color="transparent")
        other_bindings_frame.pack(fill="x")
        for row, binding in enumerate(cls.other_bindings):
            binding.newline(other_bindings_frame, row*2)

        # fps bindings
        fps_bindings_title = ctk.CTkLabel(bindings_frame, text = "FPS Bindings",
                                          text_color=colors["text"], font=fonts["h4"])
        fps_bindings_title.pack(pady=(10, 5))

        fps_bindings_frame = ctk.CTkFrame(bindings_frame, fg_color="transparent")
        fps_bindings_frame.pack(fill="x", expand=True)
        for row, binding in enumerate(cls.fps_bindings):
            binding.newline(fps_bindings_frame, row)

        def save_changes():
            cls.save_bindings()
            window.destroy()
            lift_launcher()

        save_button = ctk.CTkButton(window, text="Save Changes", text_color=colors["button text"],font=fonts["h4"],
                                    command=save_changes, fg_color=colors["primary"], hover_color=colors["primary hover"])
        save_button.pack(pady=20)

        window.protocol("WM_DELETE_WINDOW", save_changes)


class DoubleBind(Binding):
    def __init__(self):
        super().__init__(command="setbind LeftMouseButton OL_USE | setbind", description="Interaction Double Bind",
                         tooltip="Pressing that key binds both ScrollWheel and Left Mouse Button for interactions.\n"
                         "You can pass the interactions that need repeated clicking a lot faster with this. ")
        self.scroll_direction = "MouseScrollUp"  # Valeur par défaut

    def load_binding(self):
        """Charge la touche principale et la direction du scroll (Up/Down)."""
        _, line = self.file.get_line('.Bindings=(Name="', self.command)
        if line is not None:
            self.disabled = line.startswith(";-")
            parts = line.split('"')
            if len(parts) >= 2:
                self.key = parts[1]  # Récupère la première touche
            if "MouseScrollDown".lower() in line.lower():
                self.scroll_direction = "MouseScrollDown"
            else:
                self.scroll_direction = "MouseScrollUp"

    def save_binding(self):
        """Sauvegarde le binding dans le fichier."""
        prefix = ";-" if self.disabled else ""
        newline = (
            f'{prefix}.Bindings=(Name="{self.key}",Command="{self.command} {self.scroll_direction} OL_USE")'
        )
        self.file.replace_or_add(newline, ".Bindings=(", self.command)

    def change_scroll_direction(self, choice):
        """Met à jour la direction du scroll."""
        self.scroll_direction = choice

    def newline(self, parent, row):
        """Affiche deux lignes pour l'édition du DoubleBind."""
        # Première ligne : Clé principale
        self.label = ctk.CTkLabel(parent, text=self.description, font=fonts["text"], text_color=colors["text"], width=150, anchor="w")
        self.button = ctk.CTkButton(parent, text=self.key, font=fonts["text"], text_color=colors["button text"],
                                    command=self.change_binding, fg_color=colors["primary"],
                                    hover_color=colors["primary hover"], width=150)
        self.toggle = ctk.CTkSwitch(parent, text="Disabled" if self.disabled else "Enabled", font=fonts["small"], text_color=colors["text"],
                                    progress_color=colors["primary"], width=80, command=self.disable_binding)

        self.label.grid(row=row, column=0, padx=10, sticky="ew", rowspan=2)
        self.button.grid(row=row, column=1, padx=10, pady=(15, 5), sticky="ew")
        self.toggle.grid(row=row, column=2, padx=15, sticky="ew", rowspan=2)

        self.scroll_combobox = ctk.CTkOptionMenu(parent, values=["MouseScrollUp", "MouseScrollDown"], width=150,
                                                 fg_color=colors["primary"], dropdown_hover_color=colors["primary hover"],
                                                 button_hover_color=colors["secondary hover"], button_color=colors["secondary"],
                                                 command=self.change_scroll_direction)
        self.scroll_combobox.set(self.scroll_direction)
        self.scroll_combobox.grid(row=row + 1, column=1, padx=10, pady=(5, 15), sticky="ew")

        if self.tooltip:
            self.tooltip = Tooltip(parent, text=self.tooltip, shade=1)
            self.tooltip.grid(row=row, column=3, padx=10, pady=5, sticky="ew", rowspan=2)

        if not self.disabled:
            self.toggle.select()
        else:
            self.toggle.deselect()
