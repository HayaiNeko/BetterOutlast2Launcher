import customtkinter as ctk
import subprocess
import os
import math
import time
import threading

# 🔹 Configuration de l'interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 🔹 Chemins et IDs
APP_ID = "414700"  # Outlast 2
DEPOT_ID = "414701"  # Fichiers Windows
MANIFEST_ID = "7085410466650398118"  # Version du 10 mai 2017

# 🔹 Dossiers Steam et Outlast 2
STEAM_CONTENT_PATH = rf"C:\Program Files (x86)\Steam\steamapps\content\app_{APP_ID}\depot_{DEPOT_ID}"

# 🔹 Fonction pour obtenir la taille d'un dossier
def get_folder_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except Exception as e:
                print(f"Erreur sur {fp} : {e}")
    return total

# 🔹 Fonction pour ouvrir la console Steam
def open_steam_console():
    subprocess.run("start steam://open/console", shell=True)

# 🔹 Suivre la progression du téléchargement
def track_download():
    # Obtenir la taille du dossier Outlast 2 actuel
    expected_size = 27096937514
    expected_size_gb = expected_size / (1024**3)  # Convertir en Go

    while not os.path.exists(STEAM_CONTENT_PATH):
        status_label.configure(text="📥 En attente du début du téléchargement...", text_color="orange")
        time.sleep(1)

    while True:
        total_size = get_folder_size(STEAM_CONTENT_PATH)
        progress = min(100.0, (total_size / expected_size) * 100)  # Limité à 100%

        progress_label.configure(text=f"📥 Progression : {progress:.2f}% ({total_size / (1024**3):.2f} Go / {expected_size_gb:.2f} Go)")
        progress_bar.set(progress / 100)

        print(f"total : {total_size}\nexpected: {expected_size}")

        if total_size >= expected_size:
            progress_label.configure(text="✅ Téléchargement terminé !", text_color="green")
            break

        time.sleep(1)  # Vérifie toutes les 5 secondes

# 🔹 Interface Graphique
root = ctk.CTk()
root.geometry("600x350")
root.title("Téléchargement - Ancienne version d'Outlast 2")

title_label = ctk.CTkLabel(root, text="🔽 Téléchargement d'Outlast 2 (Ancienne Version)", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

open_console_button = ctk.CTkButton(root, text="🎮 Ouvrir la console Steam", font=("Arial", 14, "bold"), command=open_steam_console)
open_console_button.pack(pady=10)

progress_label = ctk.CTkLabel(root, text="📥 En attente du début du téléchargement...", font=("Arial", 14))
progress_label.pack(pady=10)

progress_bar = ctk.CTkProgressBar(root, width=400)
progress_bar.pack(pady=10)
progress_bar.set(0)

status_label = ctk.CTkLabel(root, text="", font=("Arial", 14))
status_label.pack(pady=10)

# 🔹 Lancer le suivi du téléchargement dans un thread
threading.Thread(target=track_download, daemon=True).start()

root.mainloop()
