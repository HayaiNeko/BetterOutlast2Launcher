import os
import time
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import configparser
from ui import fonts, colors  # Using the provided fonts and colors

# 🔹 Paths and IDs
APP_ID = "414700"  # Outlast 2
DEPOT_ID = "414701"  # Windows files depot
MANIFEST_ID = "7085410466650398118"  # Manifest from 10 May 2017

# 🔹 Default Steam content folder path
STEAM_CONTENT_PATH = rf"C:\Program Files (x86)\Steam\steamapps\content\app_{APP_ID}\depot_{DEPOT_ID}"


# =============================================================================
# LauncherSettings: Gestion des réglages booléens (Close On Launch, Check For Updates)
# =============================================================================

class LauncherSettings:
    config_file = "settings.ini"
    SECTION = "Launcher Settings"  # Avec espace

    def __init__(self):
        # S'assurer que le fichier de config existe
        if not os.path.exists(LauncherSettings.config_file):
            with open(LauncherSettings.config_file, 'w') as f:
                f.write("")
        # Lecture de la configuration
        self.config = configparser.ConfigParser()
        self.config.read(LauncherSettings.config_file)
        if not self.config.has_section(LauncherSettings.SECTION):
            self.config.add_section(LauncherSettings.SECTION)
        # Chargement des réglages avec des valeurs par défaut
        self.close_on_launch = self.config.getboolean(LauncherSettings.SECTION, "Close On Launch", fallback=False)
        self.check_for_updates = self.config.getboolean(LauncherSettings.SECTION, "Check For Updates", fallback=True)
        # Variables Tkinter (créées quand la fenêtre principale est disponible)
        self.var_close = None
        self.var_updates = None

    def save(self):
        # Sauvegarde des réglages dans le fichier de config
        self.config.set(LauncherSettings.SECTION, "Close On Launch", str(self.var_close.get()))
        self.config.set(LauncherSettings.SECTION, "Check For Updates", str(self.var_updates.get()))
        with open(LauncherSettings.config_file, "w") as f:
            self.config.write(f)
        print("Launcher settings saved.")

    def display(self, master):
        container = ctk.CTkFrame(master, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=10)

        # Titre avec espace dans le nom
        title = ctk.CTkLabel(container, text="Launcher Settings",
                             font=fonts["h3"], text_color=colors["text"])
        title.pack(anchor="center", pady=(0, 10))

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


# =============================================================================
# OldPatch: Gestion du dossier Old Patch – chargement, sauvegarde et installation/gestion
# =============================================================================

class OldPatch:
    CONFIG_SECTION = "OldPatch"

    def __init__(self):
        self.config_file = LauncherSettings.config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not self.config.has_section(OldPatch.CONFIG_SECTION):
            self.config.add_section(OldPatch.CONFIG_SECTION)
        # Chargement du chemin sauvegardé (vide par défaut)
        self.path = self.config.get(OldPatch.CONFIG_SECTION, "Path", fallback="")

    def save_path(self):
        self.config.set(OldPatch.CONFIG_SECTION, "Path", self.path)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        print(f"Old Patch path saved: {self.path}")

    def is_valid_old_patch(self, path):
        """Vérifie que le dossier contient Outlast2.bat."""
        if path and os.path.isdir(path):
            bat_file_path = os.path.join(path, "Outlast2.bat")
            return os.path.isfile(bat_file_path)
        return False

    def detect_path(self):
        program_path = os.path.dirname(os.path.abspath(__file__))
        common_folder = os.path.join("steamapps", "common", "Outlast 2")
        if not program_path.endswith(common_folder):
            return ""
        steamapps_root = program_path[:-len(common_folder)].rstrip(os.sep)
        old_patch_path = os.path.join(steamapps_root, "steamapps", "content",
                                      f"app_{APP_ID}", f"depot_{DEPOT_ID}")
        return old_patch_path if os.path.isdir(old_patch_path) else ""

    def install_manage(self, master):
        self.window = ctk.CTkToplevel(master, fg_color=colors["background"])
        self.window.title("Old Patch Management")
        self.window.attributes("-topmost", True)
        self.window.geometry("500x300")

        # Nouveau titre et affichage du chemin courant
        title = ctk.CTkLabel(self.window, text="Select your Old Patch Folder",
                              font=fonts["h4"], text_color=colors["text"])
        title.pack(pady=10)

        # Affichage du chemin courant (seul le texte)
        current_path_text = self.path if self.path else "Aucun chemin défini"
        self.current_path_label = ctk.CTkLabel(self.window, text=current_path_text,
                                              font=fonts["text"], text_color=colors["text"])
        self.current_path_label.pack(pady=5)

        btn_select = ctk.CTkButton(
            self.window,
            text="📂 Select Folder",
            command=lambda: self.select_folder(self.window),
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        btn_select.pack(pady=5)

        # Section de téléchargement
        label_steam = ctk.CTkLabel(self.window, text="Or download via Steam:",
                                   font=fonts["h4"], text_color=colors["text"])
        label_steam.pack(pady=10)

        btn_steam = ctk.CTkButton(
            self.window,
            text="🎮 Open Steam Console",
            command=self.open_steam_console,
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        btn_steam.pack(pady=5)

        self.copy_steam_command_button = ctk.CTkButton(
            self.window,
            text="📋 Copy Steam Download Command",
            command=self.copy_steam_command,
            font=fonts["text"],
            fg_color=colors["primary"],
            hover_color=colors["primary hover"],
            text_color=colors["text"]
        )
        self.copy_steam_command_button.pack(pady=5)

        self.progress_label = ctk.CTkLabel(self.window, text="📥 Progress: 0.00%",
                                           font=fonts["small"], text_color=colors["text"])
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.window, progress_color=colors["primary"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        self.window.update_idletasks()
        threading.Thread(target=self.track_download, daemon=True).start()

    def select_folder(self, master):
        folder_selected = filedialog.askdirectory(title="Select Old Patch Folder", parent=master)
        if folder_selected:
            if not self.is_valid_old_patch(folder_selected):
                messagebox.showerror("Erreur", "Le dossier sélectionné n'est pas un dossier Old Patch valide.")
            else:
                self.path = folder_selected
                self.save_path()
                # Mise à jour de l'affichage du chemin sans messagebox de confirmation
                self.current_path_label.configure(text=self.path)

    def open_steam_console(self):
        subprocess.run("start steam://open/console", shell=True)

    def copy_steam_command(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(f"download_depot {APP_ID} {DEPOT_ID} {MANIFEST_ID}")
        self.window.update()
        self.copy_steam_command_button.configure(text="✅ Command Copied")

    def track_download(self):
        expected_size = 27096937514  # Taille attendue en octets
        expected_size_gb = expected_size / (1024 ** 3)
        while not os.path.exists(STEAM_CONTENT_PATH):
            self.progress_label.configure(text="📥 Waiting for download to start...", text_color="orange")
            time.sleep(1)
        try:
            while True:
                total_size = self.get_folder_size(STEAM_CONTENT_PATH)
                progress = min(100.0, (total_size / expected_size) * 100)
                self.progress_label.configure(
                    text=f"📥 Progress: {progress:.2f}% ({total_size / (1024 ** 3):.2f} GB / {expected_size_gb:.2f} GB)",
                    text_color=colors["text"]
                )
                self.progress_bar.set(progress / 100)
                if total_size >= expected_size:
                    self.progress_label.configure(text="✅ Download complete!", text_color="green")
                    self.path = STEAM_CONTENT_PATH
                    self.save_path()
                    threading.Thread(target=self.try_update_demo_path, daemon=True).start()
                    break
                time.sleep(1)
        except Exception as e:
            print(e)

    def try_update_demo_path(self):
        start_time = time.time()
        while time.time() - start_time < 30:
            new_path = self.detect_path()
            if new_path and self.is_valid_old_patch(new_path) and new_path != self.path:
                self.path = new_path
                self.save_path()
                print("Demo path updated to:", new_path)
                return
            time.sleep(1)

    @staticmethod
    def get_folder_size(path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except Exception as e:
                    print(f"Error on {fp}: {e}")
        return total


# =============================================================================
# Interface principale
# =============================================================================

if __name__ == "__main__":
    launcher_settings = LauncherSettings()
    old_patch_manager = OldPatch()

    root = ctk.CTk()
    root.title("Launcher Settings")
    root.geometry("600x400")
    root.configure(fg_color=colors["background"])

    launcher_settings.display(root)

    def launch_old_patch_manager():
        # Ouvre toujours la fenêtre de gestion sans afficher de messagebox si le dossier est déjà valide
        old_patch_manager.install_manage(root)

    btn_old_patch = ctk.CTkButton(
        root,
        text="Manage Old Patch",
        command=launch_old_patch_manager,
        font=fonts["h4"],
        text_color=colors["text"],
        fg_color=colors["primary"],
        hover_color=colors["primary hover"]
    )
    btn_old_patch.pack(padx=10, pady=20)

    root.mainloop()
