import os
import sys
import ctypes
from files import File
from bindings import Binding
from os import path

# Path for PyInstaller files
if getattr(sys, 'frozen', False):  # If running as a PyInstaller bundle
    BASE_PATH = sys._MEIPASS

    # Pyinstaller BS I have no idea how it works but this saved my life (lany the goat)
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetDllDirectoryW(None)
else:
    BASE_PATH = os.path.abspath(".")


GAME_DIRECTORY = os.getcwd()

Binding.file = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultInput.ini"))

Binding("Stat FPS", "Show FPS")

