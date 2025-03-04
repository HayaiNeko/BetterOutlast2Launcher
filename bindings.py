import customtkinter as ctk
from ui import fonts, colors
from files import File
from threading import Thread
from VKcode import get_keypress


class Binding:
    file: File = None
    demo_file: File = None
    bindings = []
    bindings_count = 0

    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description
        self.key = ""
        self.disabled = False

        self.__class__.bindings.append(self)
        self.row = self.__class__.bindings_count
        self.__class__.bindings_count += 1

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
        newline = f'{prefix}.Bindings(Name="{self.key}", Command="{self.command}")'
        self.file.replace_or_add(newline, ".Bindings(", self.command)

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
        cls.file.copy_lines(cls.demo_file)

    def wait_for_keypress(self):
        key_name = get_keypress()
        if key_name:
            self.command = key_name
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

    def newline(self, parent):
        self.label = ctk.CTkLabel(parent, text=self.description, font=fonts["text"], text_color=colors["text"])
        self.button = ctk.CTkButton(parent, text=self.key, font=fonts["text"], text_color=colors["button text"],
                                    command=self.change_binding)
        self.toggle = ctk.CTkSwitch(parent, text="Disabled" if self.disabled else "Enabled", font=fonts["small"], text_color=colors["text"],
                                    command=self.disable_binding)

        self.label.grid(row=self.row, column=0, padx=10, pady=5, sticky="ew")
        self.button.grid(row=self.row, column=1, padx=10, pady=5, sticky="ew")
        self.toggle.grid(row=self.row, column=2, padx=10, pady=5, sticky="ew")

        if not self.disabled:
            self.toggle.select()
        else:
            self.toggle.deselect()

    @classmethod
    def show_bindings(cls, window, lift_launcher):
        window.title("Configure Bindings")
        window.attributes('-topmost', True)
        window_width = 520
        window_height = 100 + min(cls.bindings_count, 10) * 40
        window.geometry(f"{window_width}x{window_height}")

        title = ctk.CTkLabel(window, text="Configure Bindings", text_color=colors["text"], font=fonts["h2"])
        title.pack(pady=10)

        bindings_frame = ctk.CTkScrollableFrame(window)
        bindings_frame.pack(fill="both",expand=True, padx=10, pady=20)

        cls.load_bindings()
        for binding in cls.bindings:
            binding.newline(bindings_frame)

        def save_changes():
            cls.save_bindings()
            window.destroy()
            lift_launcher()

        save_button = ctk.CTkButton(window, text="Save Changes", text_color=colors["button text"],font=fonts["h3"],
                                    command=save_changes)
        save_button.pack(pady=10)

        window.protocol("WM_DELETE_WINDOW", save_changes)

