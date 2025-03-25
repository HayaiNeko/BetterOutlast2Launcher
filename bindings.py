import customtkinter as ctk
import bisect
from ui import fonts, colors
from files import File
from threading import Thread
from VKcode import get_keypress
from widgets import Tooltip, DeleteButton, DeletePlaceHolder
from tkinter import messagebox


class Binding:
    file: File = None
    demo_file: File = None
    bindings = []
    instances = []
    window = None
    bindings_frame = None
    lift_launcher = None

    section_bindings_frame = None

    def __init__(self, command: str, description: str, tooltip: str = None, deletable: bool = True):
        self.command = command
        self.description = description
        self.tooltip_text = tooltip
        self.key = ""
        self.deletable = deletable

        self.__class__.bindings.append(self)

    def load_binding(self):
        _, line = self.file.get_line('.Bindings=(Name="', self.command)
        if line is not None:
            self.key = line.split('"')[1]
            return
        self.key = ""

    def save_binding(self):
        newline = f'.Bindings=(Name="{self.key}",Command="{self.command}")'
        self.file.replace_or_add(newline, '.Bindings=(Name="', self.command)

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
        """Invite l’utilisateur à appuyer sur une touche pour changer le binding."""
        self.button.configure(text=">...<")
        Thread(target=self.wait_for_keypress, daemon=True).start()

    def remove_binding(self):
        """Masque puis supprime le widget correspondant au binding."""
        if self in self.__class__.instances:
            self.file.remove_line(".Bindings=(", self.command)
            Binding.bindings.remove(self)
            self.__class__.instances.remove(self)
            self.container.grid_forget()
            self.container.destroy()

    def newline(self, parent, row):
        """
        Affiche une ligne de binding dans un container.
        Le container contient le label, le bouton pour changer le binding,
        et le bouton de suppression (DeleteButton).
        """
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.container.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
        self.container.columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self.container, text=self.description, font=fonts["text"],
            text_color=colors["text"], width=180, anchor="w"
        )
        self.button = ctk.CTkButton(
            self.container, text=self.key if self.key else "",
            font=fonts["text"], text_color=colors["button text"],
            command=self.change_binding, fg_color=colors["primary"],
            hover_color=colors["primary hover"], width=150,
        )

        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.button.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        if self.tooltip_text:
            self.tooltip = Tooltip(self.container, text=self.tooltip_text, shade=1)
            self.tooltip.grid(row=0, column=2, padx=(20, 0), pady=5, sticky="ew")
        else:
            #placeholder
            self.tooltip = ctk.CTkFrame(self.container, width=24, height=24, fg_color="transparent")
            self.tooltip.grid(row=0, column=2, padx=(20, 0), pady=5, sticky="ew")

        if self.deletable:
            self.delete_button = DeleteButton(self.container, background_color=colors["background_shade1"],
                                              command=self.remove_binding)
            self.delete_button.grid(row=0, column=3, padx=15, pady=0, sticky="ew")

            for widget in (self.container, self.label, self.tooltip, self.button):
                widget.bind("<Enter>", lambda e: self.delete_button.on_enter(e))
                widget.bind("<Leave>", lambda e: self.delete_button.on_leave(e))
        else:
            self.delete_placeholder = DeletePlaceHolder(self.container, background_color=colors["background_shade1"])
            self.delete_placeholder.grid(row=0, column=3, padx=15, pady=0, sticky="ew")

    @classmethod
    def show_bindings_section(cls, title: str, bindings: list, add_button_text: str = None):
        section_frame = ctk.CTkFrame(cls.bindings_frame, fg_color="transparent")
        section_frame.pack(pady=10)
        section_title = ctk.CTkLabel(section_frame, text=title,
                                     text_color=colors["text"], font=fonts["h4"])
        section_title.pack(pady=5)

        section_bindings_frame = ctk.CTkFrame(section_frame, fg_color="transparent", height=0)
        section_bindings_frame.pack(fill="x")
        for row, binding in enumerate(bindings):
            binding.newline(section_bindings_frame, row)

        if add_button_text is not None:
            add_button = ctk.CTkButton(section_frame, font=fonts["text"], text_color=colors["text"],
                                       fg_color=colors["primary"], hover_color=colors["primary hover"],
                                       width=180, height=32,
                                       text=add_button_text, command=cls.add_binding)
            add_button.pack(pady=10)

        return section_bindings_frame

    @classmethod
    def update_ui(cls):
        if cls.section_bindings_frame:
            for widget in cls.section_bindings_frame.winfo_children():
                widget.destroy()
            for row, binding in enumerate(cls.instances):
                binding.newline(cls.section_bindings_frame, row)

    @classmethod
    def add_binding(cls):
        pass

    @classmethod
    def show_bindings(cls):
        FPSBinding.show_section()
        MiscBinding.show_section()
        SpeedrunHelperBinding.show_section()
        OptionalBinding.show_section()

    @classmethod
    def show_window(cls):
        title = ctk.CTkLabel(cls.window, text="Configure Bindings", text_color=colors["text"], font=fonts["h2"])
        title.pack(pady=10)

        cls.bindings_frame = ctk.CTkScrollableFrame(
            cls.window, fg_color=colors["background_shade1"],
            scrollbar_button_hover_color=colors["secondary hover"],
            scrollbar_button_color=colors["secondary"]
        )
        cls.bindings_frame.pack(fill="both", expand=True, padx=10, pady=(20, 0))

        cls.load_bindings()
        cls.show_bindings()

        def save_changes():
            cls.save_bindings()
            cls.window.destroy()
            cls.window = None
            cls.lift_launcher()

        save_button = ctk.CTkButton(
            cls.window, text="Save Changes", text_color=colors["button text"], font=fonts["h4"],
            command=save_changes, fg_color=colors["primary"], hover_color=colors["primary hover"]
        )
        save_button.pack(pady=20)

        cls.window.protocol("WM_DELETE_WINDOW", save_changes)


class MiscBinding(Binding):
    instances = []
    title = "Misc. Bindings"

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip, deletable=False)
        self.__class__.instances.append(self)

    @classmethod
    def show_section(cls):
        super().show_bindings_section(cls.title, cls.instances)


class DoubleBind(MiscBinding):
    def __init__(self):
        super().__init__(
            command="setbind LeftMouseButton OL_USE | setbind",
            description="Second Bind for\n Interaction",
            tooltip=("Pressing that key binds both ScrollWheel and Left Mouse Button for interactions.\n"
                     "You can pass the interactions that need repeated clicking a lot faster with this. "),
        )
        self.scroll_direction = "MouseScrollUp"  # Valeur par défaut

    def load_binding(self):
        """Charge la touche principale et la direction du scroll (Up/Down)."""
        _, line = self.file.get_line('.Bindings=(Name="', self.command)
        if line is not None:
            parts = line.split('"')
            if len(parts) >= 2:
                self.key = parts[1]
            if "mousescrolldown" in line.lower():
                self.scroll_direction = "MouseScrollDown"
            else:
                self.scroll_direction = "MouseScrollUp"

    def save_binding(self):
        newline = (
            f'.Bindings=(Name="{self.key}",Command="{self.command} {self.scroll_direction} OL_USE")'
        )
        self.file.replace_or_add(newline, ".Bindings=(", self.command)

    def change_scroll_direction(self, choice):
        self.scroll_direction = choice

    def newline(self, parent, row):
        """
        Affiche deux lignes pour l’édition du DoubleBind dans un container.
        La première ligne contient la clé et le switch (pour activer/désactiver),
        et la deuxième permet de choisir la direction du scroll.
        """
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.container.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        self.label = ctk.CTkLabel(
            self.container, text=self.description, font=fonts["text"],
            text_color=colors["text"], width=180, anchor="w"
        )
        self.button = ctk.CTkButton(
            self.container, text=self.key if self.key else "",
            font=fonts["text"], text_color=colors["button text"],
            command=self.change_binding, fg_color=colors["primary"],
            hover_color=colors["primary hover"], width=150
        )

        self.label.grid(row=0, column=0, rowspan=2, padx=10, pady=(15, 5), sticky="ew")
        self.button.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="ew")

        self.scroll_combobox = ctk.CTkOptionMenu(
            self.container, values=["MouseScrollUp", "MouseScrollDown"], width=150,
            fg_color=colors["primary"], dropdown_hover_color=colors["primary hover"],
            button_hover_color=colors["secondary hover"], button_color=colors["secondary"],
            command=self.change_scroll_direction
        )
        self.scroll_combobox.set(self.scroll_direction)
        self.scroll_combobox.grid(row=1, column=1, padx=10, pady=(5, 15), sticky="ew")

        if self.tooltip_text:
            self.tooltip = Tooltip(self.container, text=self.tooltip_text, shade=1)
            self.tooltip.grid(row=0, column=2, rowspan=2, padx=(20, 0), pady=5, sticky="ew")
        else:
            self.placeholder = ctk.CTkFrame(self.container, width=24, height=24, fg_color="transparent")
            self.placeholder.grid(row=0, column=2, rowspan=2, padx=(20, 0), pady=5, sticky="ew")

        self.delete_placeholder = DeletePlaceHolder(self.container, background_color=colors["background_shade1"])
        self.delete_placeholder.grid(row=0, column=3, padx=15, pady=0, sticky="ew")


class FPSBinding(Binding):
    fps_values = set()
    instances = [Binding(command="Stat FPS", description="Show FPS", deletable=False)]
    title = "FPS Bindings"
    section_bindings_frame = None

    def __init__(self, fps: int):
        super().__init__(command=f"Set OLEngine MaxSmoothedFrameRate {fps}", description=f"Set max FPS to {fps}")
        self.fps_value = fps
        bisect.insort(self.__class__.instances, self)

    def __lt__(self, other):
        if hasattr(other, "fps_value"):
            return self.fps_value < other.fps_value
        return False

    @classmethod
    def show_section(cls):
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances, "Add FPS Binding")

    @classmethod
    def add_binding(cls):
        def on_submit():
            try:
                fps = int(entry.get())
                FPSBinding(fps)
                window.destroy()
                cls.update_ui()
            except ValueError:
                messagebox.showerror('Error', 'Please enter a valid number.')

        window = ctk.CTkToplevel()
        window.title('Add FPS Binding')
        window.geometry('300x150')
        window.configure(bg=colors['background'])
        window.attributes('-topmost', True)

        label = ctk.CTkLabel(window, text='Enter your FPS value:', font=fonts['text'], fg_color=colors['background'])
        label.pack(pady=10)

        entry = ctk.CTkEntry(window)
        entry.pack(pady=5)

        submit_button = ctk.CTkButton(
            window,
            text='Add   ',
            command=on_submit,
            fg_color=colors['primary'],
            hover_color=colors['primary hover'],
            font=fonts['text']
        )
        submit_button.pack(pady=10)

    @classmethod
    def load_fps_values(cls):
        fps_lines = cls.file.get_lines("Set OLEngine MaxSmoothedFrameRate ")
        if not fps_lines:
            cls.fps_values = {3, 5, 8, 30, 60, 75, 105, 120, 144, 1000}

        for line in fps_lines:
            fps_part = line.lower().split('set olengine maxsmoothedframerate ')[1].split('"')[0]
            try:
                fps_value = int(fps_part)
                cls.fps_values.add(fps_value)
            except ValueError:
                print(f"[ERROR] Couldn't convert the fps value to int in {line}")

        for fps in cls.fps_values:
            FPSBinding(fps)


class SpeedrunHelperBinding(Binding):
    instances = []
    title = "Speedrun Helper Bindings"

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip, deletable=False)
        self.__class__.instances.append(self)

    @classmethod
    def show_section(cls):
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances, "Add FPS Binding")


class OptionalBinding(Binding):
    instances = []
    title = "Optional Bindings"
    section_bindings_frame = None

    # Predefined list of optional bindings stored as a class attribute
    default_bindings = [
        ("OptionalCommand1", "Description for OptionalCommand1"),
        ("OptionalCommand2", "Description for OptionalCommand2"),
        ("OptionalCommand3", "Description for OptionalCommand3"),
    ]

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip)
        self.__class__.instances.append(self)

    @classmethod
    def load_optional_bindings(cls):
        """
        Iterate through the predefined list of optional bindings and, if a command is found
        in the file (case-insensitive), create an instance and load the binding.
        """
        for cmd, desc in cls.default_bindings:
            if cls.file:
                # Search without considering case
                _, line = cls.file.get_line('.Bindings=(Name="', cmd)
                if line is not None:
                    # Check if this binding has not already been added (case-insensitive comparison)
                    exists = any(b.command.lower() == cmd.lower() for b in cls.instances)
                    if not exists:
                        binding = cls(cmd, desc)
                        binding.load_binding()  # Load the associated key from the file

    @classmethod
    def show_section(cls):
        """
        Display the Optional Bindings section with an add button.
        """
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances, "Add FPS Binding")

    @classmethod
    def add_binding(cls):
        """
        Open a window to allow the addition of an optional binding from the predefined list.
        Only a binding that is not already present will be available in the dropdown menu.
        """
        # Remove from the list those that have already been added
        available_bindings = [
            (cmd, desc) for cmd, desc in cls.default_bindings
            if not any(inst.command.lower() == cmd.lower() for inst in cls.instances)
        ]
        if not available_bindings:
            messagebox.showinfo("Info", "All Optional Bindings have already been added.")
            return

        def on_submit():
            selected = option_menu.get()
            # Search in the list for the binding corresponding to the selected command
            for cmd, desc in available_bindings:
                if cmd == selected:
                    OptionalBinding(cmd, desc)
                    window.destroy()
                    cls.update_ui()
                    return

        window = ctk.CTkToplevel()
        window.title("Add Optional Binding")
        window.geometry("300x150")
        window.configure(bg=colors['background'])
        window.attributes('-topmost', True)

        label = ctk.CTkLabel(
            window,
            text="Select an Optional Binding:",
            font=fonts['text'],
            fg_color=colors['background']
        )
        label.pack(pady=10)

        # Dropdown menu offering only the bindings that haven't been added
        options = [cmd for cmd, _ in available_bindings]
        option_menu = ctk.CTkOptionMenu(
            window,
            values=options,
            width=200,
            fg_color=colors["primary"],
            dropdown_hover_color=colors["primary hover"],
            button_hover_color=colors["secondary hover"],
            button_color=colors["secondary"]
        )
        option_menu.set(options[0])
        option_menu.pack(pady=5)

        submit_button = ctk.CTkButton(
            window,
            text="Add",
            font=fonts['text'],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            command=on_submit
        )
        submit_button.pack(pady=10)
