import sys
import os
import ctypes
from widgets import show_error

# Path for PyInstaller files
if getattr(sys, 'frozen', False):  # If running as a PyInstaller bundle
    BASE_PATH = sys._MEIPASS

    # Pyinstaller BS I have no idea how it works but this saved my life (lany the goat)
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetDllDirectoryW(None)
else:
    BASE_PATH = os.path.abspath(".")

GAME_DIRECTORY = os.getcwd()

CONFIG_FILE = "LauncherConfig.ini"
OL2_ICON = os.path.join(BASE_PATH, "OutlastII_icon.png")


# Checks game directory
def check_game_folder():
    required_files = [
        "OLGame",
        "Binaries",
        "Engine",
    ]
    missing_files = [file for file in required_files if not os.path.exists(os.path.join(GAME_DIRECTORY, file))]

    if missing_files:
        show_error("The launcher is not in the correct directory. Ensure it is placed in the Outlast II game folder.")
        sys.exit(1)


check_game_folder()
