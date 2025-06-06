from paths import CONFIG_FILE
import configparser
import customtkinter as ctk
from ui import fonts, colors  # Using provided fonts and colors

class LauncherSettings:
    SECTION = "Launcher Settings"

    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not self.config.has_section(LauncherSettings.SECTION):
            self.config.add_section(LauncherSettings.SECTION)

        self.close_on_launch = self.config.getboolean(LauncherSettings.SECTION, "Close On Launch", fallback=False)
        self.check_for_updates = self.config.getboolean(LauncherSettings.SECTION, "Check For Updates", fallback=True)
        self.var_close = None
        self.var_updates = None

    def save(self):
        # Save settings to the configuration file
        self.close_on_launch = self.var_close.get()
        self.config.set(LauncherSettings.SECTION, "Close On Launch", str(self.close_on_launch))
        self.check_for_updates = self.var_updates.get()
        self.config.set(LauncherSettings.SECTION, "Check For Updates", str(self.check_for_updates))
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
                                     text="Close On Launch", text_color=colors["text"],
                                     command=self.save,
                                     progress_color=colors["primary"])
        switch_close.pack(pady=5)

        self.var_updates = ctk.BooleanVar(master=container, value=self.check_for_updates)
        switch_updates = ctk.CTkSwitch(container, variable=self.var_updates,
                                       text="Check For Updates", text_color=colors["text"],
                                       command=self.save,
                                       progress_color=colors["primary"])
        switch_updates.pack(pady=(5, 15))