from ui import fonts, colors
import customtkinter as ctk
from files import File
from widgets import Tooltip, TooltipPlaceholder


class Setting:
    def __init__(self, name: str, file: File, setting: str, enabled_value: str = "true", disabled_value: str = "false"):
        assert setting[-1] == "=", "Setting format invalid"

        self.name = name
        self.file = file
        self.setting = setting
        self.enabled_value = enabled_value.lower()
        self.disabled_value = disabled_value.lower()

    def get_value(self):
        """Récupère la valeur actuelle du paramètre dans le fichier."""
        i, line = self.file.get_line(self.setting)
        if i >= 0:
            return line.split("=")[-1].strip().lower()
        return None

    def is_enabled(self):
        """Vérifie si la valeur actuelle est celle correspondant à 'enabled'."""
        value = self.get_value()
        return value == self.enabled_value if value is not None else False

    def toggle(self):
        """Inverse la valeur actuelle entre enabled et disabled."""
        i, line = self.file.get_line(self.setting)
        if i >= 0:
            current_value = self.get_value()
            new_value = self.disabled_value if current_value == self.enabled_value else self.enabled_value
            self.file.replace_index(f"{self.setting}{new_value}", i, line)
            self.file.write_lines()

    def enable(self):
        """Active le paramètre si ce n'est pas déjà le cas."""
        if not self.is_enabled():
            self.toggle()

    def disable(self):
        if self.is_enabled():
            self.toggle()


class DisplaySetting(Setting):
    display_settings = []  # Liste spécifique pour les paramètres affichables

    def __init__(self, name: str, file, setting: str, enabled_value: str = "true",
                 disabled_value: str = "false", tooltip_text: str = ""):
        super().__init__(name, file, setting, enabled_value, disabled_value)
        self.tooltip_text = tooltip_text

        self.__class__.display_settings.append(self)  # Ajoute uniquement les DisplaySetting à la liste

    def newline(self, frame):
        """Affiche l'élément dans l'interface graphique."""
        self.container = ctk.CTkFrame(frame, fg_color="transparent")
        self.container.pack(fill="x", pady=10, padx=20)

        self.setting_label = ctk.CTkLabel(self.container, text=self.name, text_color=colors["text"], font=fonts["text"])
        self.setting_label.pack(side="left")

        self.status_label = ctk.CTkLabel(self.container, font=fonts["small"])
        self.action_button = ctk.CTkButton(self.container, text_color=colors["text"], font=fonts["small"], width=100,
                                           fg_color=colors["primary"], hover_color=colors["primary hover"],
                                           command=lambda: [self.toggle(), self.refresh_window()])

        if self.tooltip_text:
            self.tooltip = Tooltip(self.container, text=self.tooltip_text, shade=1)
        else:
            self.tooltip = TooltipPlaceholder(self.container)

        self.tooltip.pack(side="right", padx=10)
        self.action_button.pack(side="right", padx=10)
        self.status_label.pack(side="right", padx=10)

        self.refresh_window()

    def refresh_window(self):
        """Met à jour l'affichage en fonction de l'état actuel."""
        if self.is_enabled():
            status_text, status_color = "Enabled", colors["success"]
            action_text = "Disable"
        else:
            status_text, status_color = "Disabled", colors["error"]
            action_text = "Enable"

        self.status_label.configure(text=status_text, text_color=status_color)
        self.action_button.configure(text=action_text)

    @classmethod
    def show_settings(cls, window):
        """Affiche uniquement les paramètres nécessitant un affichage."""
        frame = ctk.CTkFrame(window, fg_color=colors["background_shade1"])
        frame.pack(pady=10, fill="x", padx=20)

        title = ctk.CTkLabel(frame, text="Settings", text_color=colors["text"], font=fonts["h3"])
        title.pack(pady=10)

        for setting in cls.display_settings:
            setting.newline(frame)
