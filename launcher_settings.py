import os
import configparser
import customtkinter as ctk
from ui import fonts, colors  # Using provided fonts and colors

class LauncherSettings:
    SECTION = "Launcher Settings"  # Section name with space

    def __init__(self):
        self.config_file = "LauncherConfig.ini"
        # Ensure the configuration file exists
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                f.write("")
        # Read configuration
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not self.config.has_section(LauncherSettings.SECTION):
            self.config.add_section(LauncherSettings.SECTION)
        # Load settings with default values
        self.close_on_launch = self.config.getboolean(LauncherSettings.SECTION, "Close On Launch", fallback=False)
        self.check_for_updates = self.config.getboolean(LauncherSettings.SECTION, "Check For Updates", fallback=True)
        # Tkinter variables (created when the main window is available)
        self.var_close = None
        self.var_updates = None

    def save(self):
        # Save settings to the configuration file
        self.config.set(LauncherSettings.SECTION, "Close On Launch", str(self.var_close.get()))
        self.config.set(LauncherSettings.SECTION, "Check For Updates", str(self.var_updates.get()))
        with open(self.config_file, "w") as f:
            self.config.write(f)
        print("Launcher settings saved.")

    def display(self, master):
        container = ctk.CTkFrame(master, fg_color=colors["background_shade1"])
        container.pack(fill="x", padx=10, pady=10)

        # Centered title
        title = ctk.CTkLabel(container, text="Launcher Settings",
                             font=fonts["h3"], text_color=colors["text"])
        title.pack(anchor="center", pady=20)

        self.var_close = ctk.BooleanVar(master=container, value=self.close_on_launch)
        switch_close = ctk.CTkSwitch(container, variable=self.var_close,
                                     text="Close On Launch", command=self.save,
                                     progress_color=colors["primary"])
        switch_close.pack(pady=5)

        self.var_updates = ctk.BooleanVar(master=container, value=self.check_for_updates)
        switch_updates = ctk.CTkSwitch(container, variable=self.var_updates,
                                       text="Check For Updates", command=self.save,
                                       progress_color=colors["primary"])
        switch_updates.pack(pady=5)

        return container
