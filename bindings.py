import os
import customtkinter as ctk
import bisect
from ui import fonts, colors
from files import File
from threading import Thread
from VKcode import get_keypress
from widgets import InfoIcon, InfoIconPlaceholder, DeleteButton, DeletePlaceHolder
from tkinter import messagebox
from paths import GAME_DIRECTORY, MODS_PATH
from platformdirs import user_documents_path
from mods import ReplacementMod


class Binding:
    file: File = File(os.path.join(GAME_DIRECTORY, "OLGame/Config/DefaultInput.ini"))
    demo_file: File = None
    bindings = []
    instances = []
    window = None
    bindings_frame = None
    lift_launcher = None

    section_bindings_frame = None

    def __init__(self, command: str, description: str, tooltip: str = None, deletable: bool = True):
        """
        :param command: Command triggered by the binding (e.g. "Stat FPS", "Show Collision")
        :param description: Description of what the binding does (Showed to the user)
        :param tooltip: Shows a tooltip that helps the user understand what the binding does (Optionnal)
        :param deletable: If the binding is can be deleted
        """
        self.command = command
        self.description = description
        self.tooltip_text = tooltip
        self.key = ""
        self.deletable = deletable

        self.__class__.bindings.append(self)

    def load_binding(self):
        """Loads the existing key for a binding in DefaultInput.ini (if it exists)"""
        _, line = self.file.get_line('.Bindings=(Name="',  f'Command="{self.command}"')
        if line is not None:
            self.key = line.split('"')[1]
            return
        self.key = ""

    def save_binding(self):
        """Save changes made in DefaultInput.ini"""
        newline = f'.Bindings=(Name="{self.key}",Command="{self.command}")'
        self.file.replace_or_add(newline, '.Bindings=(Name="',  f'Command="{self.command}"')

    @classmethod
    def load_bindings(cls):
        """Loads all bindings"""
        for binding in cls.bindings:
            binding.load_binding()

    @classmethod
    def save_bindings(cls):
        """Saves all changes made to bindings"""
        for binding in cls.bindings:
            binding.save_binding()
        cls.file.write_lines()

    def wait_for_keypress(self):
        """
        Helper function for change binding.
        Listens to the users keyboard and make the necessary changes accordingly
        """
        key_name = get_keypress()
        if key_name:
            self.key = key_name
            self.button.configure(text=key_name)
        else:
            self.button.configure(text="Unrecognized")

    def change_binding(self):
        """
        Called when the user clicks on a binding's button to change it.
        When a key is pressed, it is assigned to the binding.
        """
        self.button.configure(text=">...<")
        Thread(target=self.wait_for_keypress, daemon=True).start()

    def remove_binding(self):
        """Removes a binding both in the UI and logically"""
        if self in self.__class__.instances:
            self.file.remove_line(".Bindings=(", f'Command="{self.command}"')
            Binding.bindings.remove(self)
            self.__class__.instances.remove(self)
            self.container.grid_forget()
            self.container.destroy()

    def newline(self, parent, row):
        """Shows a line in the UI for the binding."""
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
            self.tooltip = InfoIcon(self.container, text=self.tooltip_text, shade=1)
        else:
            self.tooltip = InfoIconPlaceholder(self.container)
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
    def show_bindings_section(cls, title: str, bindings: list, add_button_text: str = None) -> ctk.CTkFrame:
        """
        Shows an entire section of bindings.
        A section is made of all bindings from a subclass (each subclass has a section).
        :param title: Title of the section (showed to the user)
        :param bindings: List of bindings in the section
        :param add_button_text: If bindings can be added, this is the text of the add button.
                                If set to None, there is no add button showed.
        :return: Returns the frame of the section. Used to update the section later.
        """
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
        """
        Updates the UI on a single section.
        A section is made of all bindings from a subclass (each subclass has a section).
        """
        if cls.section_bindings_frame:
            for widget in cls.section_bindings_frame.winfo_children():
                widget.destroy()
            for row, binding in enumerate(cls.instances):
                binding.newline(cls.section_bindings_frame, row)

    @classmethod
    def add_binding(cls):
        """Defined only for class of bindings that can be added"""
        pass

    @classmethod
    def show_bindings(cls):
        """Show all sections of bindings"""
        FPSBinding.show_section()
        MiscBinding.show_section()
        SpeedrunHelperBinding.show_section()
        OptionalBinding.show_section()

    @classmethod
    def show_window(cls):
        """Shows the entire UI to manage bindings on the window passed into the class"""
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
    """
    Subclass for the section of miscellaneous bindings.
    Those bindings are not deletable.
    """
    instances = []
    title = "Misc. Bindings"

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip, deletable=False)
        self.__class__.instances.append(self)

    @classmethod
    def show_section(cls):
        super().show_bindings_section(cls.title, cls.instances)


class DoubleBind(MiscBinding):
    """Class Used specifically for the DoubleBind on interaction key"""
    def __init__(self):
        super().__init__(
            command="setbind LeftMouseButton OLA_USE | setbind",
            description="Second Bind for\n Interaction",
            tooltip=("Pressing that key binds both ScrollWheel and Left Mouse Button for interactions.\n"
                     "You can pass the interactions that need repeated clicking a lot faster with this. "),
        )
        self.scroll_direction = "MouseScrollUp"  # Default Value

    def load_binding(self):
        """Loads the existing key and the scroll direction from DefaultInput.ini"""
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
        """Saves the key and scroll direction in DefaultInput.ini"""
        newline = (
            f'.Bindings=(Name="{self.key}",Command="{self.command} {self.scroll_direction} OLA_USE")'
        )
        self.file.replace_or_add(newline, ".Bindings=(", self.command)

    def change_scroll_direction(self, choice):
        """Changes the scroll direction"""
        self.scroll_direction = choice

    def newline(self, parent, row):
        """
        Shows a line in the UI for the double bind.
        Two lines need to be used to show both the key selection and scroll direction selection.
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
            self.tooltip = InfoIcon(self.container, text=self.tooltip_text, shade=1)
        else:
            self.tooltip = InfoIconPlaceholder(self.container)
        self.tooltip.grid(row=0, column=2, rowspan=2, padx=(20, 0), pady=5, sticky="ew")

        self.delete_placeholder = DeletePlaceHolder(self.container, background_color=colors["background_shade1"])
        self.delete_placeholder.grid(row=0, column=3, padx=15, pady=0, sticky="ew")


class FPSBinding(Binding):
    """
    Subclass for the section of FPS bindings.
    Those bindings are deletable and bindings for custom fps values can be added.
    """
    fps_values = set()
    # Stat FPS binding is manually added to that section
    instances = [Binding(command="Stat FPS", description="Show FPS", deletable=False)]
    title = "FPS Bindings"
    section_bindings_frame = None

    def __init__(self, fps: int):
        """Creates a binding with the command to set the fps to a given value"""
        super().__init__(command=f"Set OLEngine MaxSmoothedFrameRate {fps}", description=f"Set max FPS to {fps}")
        self.fps_value = fps
        bisect.insort(self.__class__.instances, self)

    def __lt__(self, other):
        """Used to access sorting functions"""
        # Check if other is an instance of FPSBinding
        if hasattr(other, "fps_value"):
            return self.fps_value < other.fps_value
        return False

    @classmethod
    def show_section(cls):
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances, "Add FPS Binding")

    @classmethod
    def add_binding(cls):
        """Creates a window that asks a custom fps value to the user and then adds it to the list."""
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
        window.configure(fg_color=colors['background'])
        window.attributes('-topmost', True)

        label = ctk.CTkLabel(window, text='Enter your FPS value:', font=fonts['text'])
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
        """
        Load existing fps bindings if they exist in DefaultInput.ini.
        If there are none, a default set of recommended fps values is used.
        """
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
    """
    Subclass for the section of bindings related to Speedrunhelper.
    Those bindings are not deletable.
    """

    instances = []
    title = "Speedrun Helper Bindings"

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip, deletable=False)
        self.__class__.instances.append(self)

    @classmethod
    def show_section(cls):
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances)


class OptionalBinding(Binding):
    """
    Subclass for the section of FPS bindings.
    Those bindings are deletable and custom commands can be added (from a predefined list).
    """

    instances = []
    title = "Optional Bindings"
    section_bindings_frame = None
    default_bindings: list = []
    available_bindings: list = []

    def __init__(self, command, description, tooltip=None):
        super().__init__(command, description, tooltip)
        self.__class__.instances.append(self)

    @classmethod
    def load_optional_bindings(cls):
        """
        Iterate through the predefined list of optional bindings and, if a command is found
        in the file, create an instance of the binding.
        """
        for cmd, desc in DevConsoleBinding.dev_bindings:
            if cls.file:
                _, line = cls.file.get_line(cmd)
                if line is not None:
                    if line[0] != ";":
                        exists = any(binding.command.lower() == cmd.lower() for binding in cls.instances)
                        if not exists:
                            DevConsoleBinding(cmd, desc)

        for cmd, desc in cls.default_bindings:
            if cls.file:
                _, line = cls.file.get_line('.Bindings=(Name="', cmd)
                if line is not None:
                    # Check if this binding has not already been added (case-insensitive comparison)
                    exists = any(binding.command.lower() == cmd.lower() for binding in cls.instances)
                    if not exists:
                        OptionalBinding(cmd, desc)

    @classmethod
    def show_section(cls):
        cls.section_bindings_frame = super().show_bindings_section(cls.title, cls.instances, "Add Optional Binding")

    @classmethod
    def add_binding(cls):
        """
        Open a window to allow the addition of an optional binding from the predefined list.
        Only a binding that is not already present will be available in the dropdown menu.
        """
        cls.available_bindings = [
                                     (cmd, desc) for cmd, desc in DevConsoleBinding.dev_bindings
                                     if not any(inst.command.lower() == cmd.lower() for inst in cls.instances)
                                 ] + [
                                     (cmd, desc) for cmd, desc in cls.default_bindings
                                     if not any(inst.command.lower() == cmd.lower() for inst in cls.instances)
                                 ]

        if not cls.available_bindings:
            messagebox.showinfo("Info", "All Optional Bindings have already been added.")
            return

        def on_submit():
            selected = option_menu.get()

            for cmd, desc in cls.available_bindings:
                if desc == selected:

                    is_dev_console = any(c == cmd for c, d in DevConsoleBinding.dev_bindings)
                    if is_dev_console:
                        DevConsoleBinding(cmd, desc)
                    else:
                        OptionalBinding(cmd, desc)

                    window.destroy()
                    cls.update_ui()
                    return

        window = ctk.CTkToplevel()
        window.title("Add Optional Binding")
        window.geometry("300x150")
        window.configure(fg_color=colors['background'])
        window.attributes('-topmost', True)

        label = ctk.CTkLabel(
            window,
            text="Select an Optional Binding:",
            font=fonts['text']
        )
        label.pack(pady=10)

        # Dropdown menu offering only the bindings that haven't been added
        options = [desc for _, desc in cls.available_bindings]
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


class DevConsoleBinding(OptionalBinding):
    engine_upk = ReplacementMod(name="engine.upk",
                                mod_source_path=os.path.join(MODS_PATH, "EngineUPK", "Modded"),
                                original_source_path=os.path.join(MODS_PATH, "EngineUPK", "Orignal"),
                                install_path=os.path.join(GAME_DIRECTORY, "OLGame", "CookedPCConsole"))

    dev_bindings = [
        ("TypeKey=", "UE Console"),
        ("ConsoleKey=", "Detailed Console")
    ]

    @classmethod
    def enable_console(cls):
        # install modded engine.upk that enables the console
        if not cls.engine_upk.is_installed():
            cls.engine_upk.install()

        # Disable alt key to open the console
        Binding.file.remove_line("TypeKeyAlt")
        Binding.file.write_lines()

    def __init__(self, command, description):
        super().__init__(command, description)

    def load_binding(self):
        """Loads the existing key for a binding in DefaultInput.ini (if it exists)"""
        _, line = self.file.get_line(self.command)
        if line is not None:
            self.key = line.split('=')[1]
            return
        self.key = ""

    def save_binding(self):
        """Save changes made in DefaultInput.ini"""
        newline = f'{self.command}{self.key}'
        self.file.replace_line(newline, self.command)

    def remove_binding(self):
        """Removes a binding both in the UI and logically"""
        if self in self.__class__.instances:
            self.file.replace_term(self.command, f";{self.command}")
            Binding.bindings.remove(self)
            self.__class__.instances.remove(self)
            self.container.grid_forget()
            self.container.destroy()
