import sys
import os
import ctypes
import zipfile
import tempfile
from widgets import show_error

# ---------------------------------------------------------------------------
#  PyInstaller runtime paths
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False):                 # Running as a PyInstaller bundle
    BASE_PATH = sys._MEIPASS                     # Folder where data files are unpacked

    # PyInstaller BS I have no idea how it works but this saved my life (lany the goat)
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetDllDirectoryW(None)
else:
    BASE_PATH = os.path.abspath(".")

# ---------------------------------------------------------------------------
#  Main Paths
# ---------------------------------------------------------------------------
GAME_DIRECTORY = os.getcwd()
CONFIG_FILE = "LauncherConfig.ini"
OL2_ICON = os.path.join(BASE_PATH, "OutlastII_icon.png")

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def check_game_folder() -> None:
    """Verify that the launcher is located in the Outlast II installation folder."""
    required = ["OLGame", "Binaries", "Engine"]
    missing  = [f for f in required if not os.path.exists(os.path.join(GAME_DIRECTORY, f))]

    if missing:
        show_error(
            "The launcher is not in the correct directory.\n"
            "Place it inside the Outlast II game folder."
        )
        sys.exit(1)

def extract_mods() -> str:
    """
    Extract Mods.zip (bundled with PyInstaller) to %TEMP%/outlast2_mods
    and return the absolute path. Returns None if extraction fails.
    """
    mods_zip  = os.path.join(BASE_PATH, "Mods.zip")
    temp_root = os.path.join(tempfile.gettempdir(), "outlast2_mods")

    # Skip extraction if we already did it this session
    if not os.path.exists(temp_root):
        try:
            os.makedirs(temp_root, exist_ok=True)
            with zipfile.ZipFile(mods_zip, "r") as zf:
                zf.extractall(temp_root)
            print(f"Mods extracted successfully to {temp_root}")
        except Exception as exc:
            show_error(f"Failed to extract Mods.zip: {exc}")
            sys.exit(1)

    return temp_root


# ---------------------------------------------------------------------------
#  Main sequence
# ---------------------------------------------------------------------------
check_game_folder()

# Extracting mods into temporary folder
MODS_PATH = extract_mods()
