import customtkinter as ctk
import subprocess
import webbrowser
import pyperclip

# 🔹 Configuration de l'interface CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 🔹 Définition des IDs du jeu
APP_ID = "414700"  # Outlast 2
DEPOT_ID = "414701"  # Fichiers Windows
MANIFEST_ID = "7085410466650398118"  # Version du 10 mai 2017

# 🔹 Commande Steam à exécuter
STEAM_COMMAND = f"download_depot {APP_ID} {DEPOT_ID} {MANIFEST_ID}"

# 🔹 Fonction pour ouvrir la console Steam
def open_steam_console():
    webbrowser.open("steam://open/console")

# 🔹 Fonction pour copier la commande dans le presse-papier et informer l'utilisateur
def copy_steam_command():
    pyperclip.copy(STEAM_COMMAND)  # Copie la commande dans le presse-papier
    status_label.configure(text="✅ Commande copiée ! Collez-la dans la console Steam.", text_color="green")

# 🔹 Créer la fenêtre principale
root = ctk.CTk()
root.geometry("500x250")
root.title("Téléchargement - Ancienne version d'Outlast 2")

# 🔹 Ajouter un titre
title_label = ctk.CTkLabel(root, text="🔽 Téléchargeur d'anciennes versions d'Outlast 2", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# 🔹 Bouton pour ouvrir la console Steam
open_console_button = ctk.CTkButton(root, text="🎮 Ouvrir la console Steam", font=("Arial", 14, "bold"), command=open_steam_console)
open_console_button.pack(pady=10)

# 🔹 Bouton pour copier la commande Steam
copy_command_button = ctk.CTkButton(root, text="📋 Copier la commande Steam", font=("Arial", 14, "bold"), command=copy_steam_command)
copy_command_button.pack(pady=10)

# 🔹 Label de statut
status_label = ctk.CTkLabel(root, text="🔍 Ouvrez la console Steam et exécutez la commande.", font=("Arial", 14))
status_label.pack(pady=10)

# 🔹 Lancer l'application
root.mainloop()
