import os
import sys
import ctypes
from files import File
from bindings import Binding, DoubleBind
from settings import Setting, DisplaySetting
from mods import Mod, LWMod, DisplayMod
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

Binding.file = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultInput.ini"))

Binding(command="Stat FPS", description="Show FPS", tooltip="this is a tooltip look")
ol_menu_bind = Binding(command="OLA_ShowMenu", description="Open Outlast Menu")
ol_menu_bind.disabled = True
DoubleBind()

fps_lines = Binding.file.get_lines(".Bindings(", "Set OLEngine MaxSmoothedFrameRate")
fps_values = {3, 5, 8, 30, 60, 75, 105, 120, 144, 1000}

for line in fps_lines:
    if 'set olengine maxsmoothedframerate' in line.lower():
        parts = line.lower().split('set olengine maxsmoothedframerate ')
        if len(parts) > 1:
            fps_part = parts[1].split('"')[0]
            try:
                fps_value = int(fps_part)
                fps_values.add(fps_value)
            except ValueError:
                print([f"[ERROR] Couldn't convert the fps value to int in {line}"])

# Conversion en liste triée
fps_values = sorted(fps_values)

for fps in fps_values:
    Binding(command=f"Set OLEngine MaxSmoothedFrameRate {fps}", description=f"Set max FPS to {fps}")


default_game = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultGame.ini"))
stamina_off = Setting("StaminaOff",
                      file=default_game,
                      setting="StaminaMaxStamina=",
                      enabled_value="-1", disabled_value="100")
sprint_delay_off = Setting("SprintDelayOff",
                           file=default_game,
                           setting="SprintDelay=",
                           enabled_value="0", disabled_value="2")

DisplaySetting("Launch with Steam",
               File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultEngine.ini")),
               "bRelaunchInSteam=")
DisplaySetting("Borderless Windowed",
               File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultSystemSettings.ini")),
               "UseBorderlessFullscreen=", enabled_value="false", disabled_value="true")
DisplaySetting("Pause on Loss of Focus",
               File(path.join(GAME_DIRECTORY, "OLGame", "Config", "OLEngine.ini")),
               "bPauseOnLossOfFocus=")
DisplaySetting("Mouse Smoothing",
               Binding.file,
               "bEnableMouseSmoothing=")

Mod("ModLoader",
    (path.join(BASE_PATH, "Mods", "ModLoader"), path.join(GAME_DIRECTORY, "Binaries", "Win64")))

LWMod("No CPK",
      (path.join(BASE_PATH, "Mods", "No CPK"),path.join(GAME_DIRECTORY, "Mods")),
      sprint_delay_off)
LWMod("Cutscene Skip",
      (path.join(BASE_PATH, "Mods", "Cutscene Skip"), path.join(GAME_DIRECTORY, "Mods")))

LWMod("No Stamina",
      None,
      stamina_off, sprint_delay_off)

DisplayMod("Speedrun Helper",
           (path.join(BASE_PATH, "Mods", "Speedrun Helper"), path.join(GAME_DIRECTORY, "Mods")))






