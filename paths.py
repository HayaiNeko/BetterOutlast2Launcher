import os
import sys
import ctypes
from files import *
from bindings import *
from settings import *
from widgets import show_error
from mods import Mod, LWMod, DisplayMod
from old_patch import OldPatch
from launcher_settings import LauncherSettings
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

# Files
Binding.file = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultInput.ini"))

default_game = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultGame.ini"))
stamina_off = Setting("StaminaOff",
                      file=default_game,
                      setting="StaminaMaxStamina=",
                      enabled_value="-1", disabled_value="100")
sprint_delay_off = Setting("SprintDelayOff",
                           file=default_game,
                           setting="SprintDelay=",
                           enabled_value="0", disabled_value="2")

# Bindings
ol_menu_bind = MiscBinding(command="OLA_ShowMenu", description="Open Outlast Menu",
                              tooltip="Bind a custom to key to open the menu.")
MiscBinding(command="abc", description='abc')
DoubleBind()
MiscBinding(command="Displayall OLHero Rotation", description="Show Rotation")

SpeedrunHelperBinding(command="BOL Toggle Freecam", description="Toggle Freecam")
SpeedrunHelperBinding(command="BOL TP to Freecam", description="TP to Freecam")
SpeedrunHelperBinding(command="BOL Toggle GodMode", description="Toggle GodMode")
SpeedrunHelperBinding(command="BOL Show Player Info", description="Show Player Info")

FPSBinding.load_fps_values()

# Settings
Steam = DisplaySetting("Launch with Steam",
                       File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultEngine.ini")),
                       "bRelaunchInSteam=")
Vsync = DisplaySetting("Vsync",
                       File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultSystemSettings.ini")),
                       "SyncInterval=", enabled_value="1", disabled_value="0")
Borderless = DisplaySetting("Borderless Windowed",
                            File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultSystemSettings.ini")),
                            "UseBorderlessFullscreen=", enabled_value="false", disabled_value="true")
bPause = DisplaySetting("Pause on Loss of Focus",
                        File(path.join(GAME_DIRECTORY, "OLGame", "Config", "OLEngine.ini")),
                        "bPauseOnLossOfFocus=")
MouseSmoothing = DisplaySetting("Mouse Smoothing",
                                Binding.file,
                                "bEnableMouseSmoothing=")

# Mods
ModLoader = Mod("ModLoader",
                (path.join(BASE_PATH, "Mods", "ModLoader"), path.join(GAME_DIRECTORY, "Binaries", "Win64")))

NoCPK = LWMod("No CPK",
              (path.join(BASE_PATH, "Mods", "No CPK"),path.join(GAME_DIRECTORY, "Mods")),
              sprint_delay_off)
CutsceneSkip = LWMod("Cutscene Skip",
                     (path.join(BASE_PATH, "Mods", "Cutscene Skip"), path.join(GAME_DIRECTORY, "Mods")))

NoStamina = LWMod("No Stamina",
                  None,
                  stamina_off, sprint_delay_off)

SpeedrunHelper = DisplayMod("Speedrun Helper",
                            (path.join(BASE_PATH, "Mods", "Speedrun Helper"), path.join(GAME_DIRECTORY, "Mods")))


def first_launch():
    ModLoader.install()
    SpeedrunHelper.install()
    Steam.disable()
    Vsync.disable()
    Borderless.enable()
    bPause.disable()


if not os.path.exists("LauncherConfig.ini"):
    first_launch()

LauncherSettings = LauncherSettings()
OldPatch = OldPatch()
