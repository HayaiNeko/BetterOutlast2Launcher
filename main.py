# Compile command: pyinstaller --onefile --name BetterOutlast2Launcher --icon=OutlastII_icon.png --add-data "Mods.zip;." --add-data "OutlastII_icon.png;." main.py --noconsole

import os
from paths import GAME_DIRECTORY, MODS_PATH
from files import File
from bindings import DoubleBind, MiscBinding, SpeedrunHelperBinding, FPSBinding, OptionalBinding
from settings import Setting, DisplaySetting
from mods import LWMod, DisplayMod
from updates import LauncherUpdater
from os import path
from launcher import Launcher

CURRENT_VERSION = "1.1.4"

# Files
default_game = File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultGame.ini"))
stamina_off = Setting("StaminaOff",
                      file=default_game,
                      setting="StaminaMaxStamina=",
                      enabled_value="-1", disabled_value="100")
sprint_delay_off = Setting("SprintDelayOff",
                           file=default_game,
                           setting="SprintDelay=",
                           enabled_value="0", disabled_value="2")
LWMod.sprint_delay = Setting("SprintDelay",
                          file=default_game,
                          setting="SprintDelay=",
                          enabled_value="2", disabled_value="0")

# Bindings
DoubleBind()
MiscBinding(command="DisplayAll OLHero Rotation", description="Show Rotation")
MiscBinding(command="Set OLGame DifficultyMode EDMO_Insane", description="Set Difficulty to Insane")

SpeedrunHelperBinding(command="BOL ToggleFreeCam", description="Toggle Freecam")
SpeedrunHelperBinding(command="BOL TeleportToFreeCam", description="Teleport to Freecam")
SpeedrunHelperBinding(command="BOL ToggleGodMode", description="Toggle GodMode")


FPSBinding.load_fps_values()

OptionalBinding.default_bindings = [
    ("Set OLGame CurrentCheckpointName None", "Set Checkpoint to None"),
    ("Set OLHero StaminaMaxStamina -1", "Enable Infinite Stamina"),
    ("Set OLHero StaminaMaxStamina -1 | Set OLHero SprintDelay 0", "Enable No Stamina Settings"),
    ("Set OLHero StaminaMaxStamina 100 | Set OLHero SprintDelay 2", "Disable No Stamina Settings"),
    ("DisplayAll OLHero StaminaMaxStamina | Displayall OLHero SprintDelay", "Show Stamina/SprintDelay"),
    ("DisplayAll OLHero Location", "Show Location"),
    ("DisplayAll OLHero Velocity", "Show Velocity"),
    ("nxvis collision", "Show Collision"),
    ("Set OLGame CurrentCheckpointName None | StreamMap minefacility_persistent", "Judges Skip")
]

OptionalBinding.load_optional_bindings()

# Settings
Steam = DisplaySetting("Launch with Steam",
                       File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultEngine.ini")),
                       "bRelaunchInSteam=",
                       tooltip_text="Launches the game with Steam.\n"
                                    "Disabled is recommended.")
Vsync = DisplaySetting("Vsync",
                       File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultSystemSettings.ini")),
                       "SyncInterval=", enabled_value="1", disabled_value="0",
                       tooltip_text="Enabling Vsync renders max framerate changes impossible.\n"
                                    "Disabled is recommended")
Borderless = DisplaySetting("Borderless Windowed",
                            File(path.join(GAME_DIRECTORY, "OLGame", "Config", "DefaultSystemSettings.ini")),
                            "UseBorderlessFullscreen=",
                            tooltip_text="Enables Borderless Windowed.\n"
                                         "Recommended for less laggy alt tabs and to see your livesplit.")
bPause = DisplaySetting("Pause on Loss of Focus",
                        File(path.join(GAME_DIRECTORY, "Engine", "Config", "BaseEngine.ini")),
                        "bPauseOnLossOfFocus=",
                        tooltip_text="If disabled, game will not be paused during alt tabs.")
MouseSmoothing = DisplaySetting("Mouse Smoothing",
                                File(path.join(GAME_DIRECTORY, "Engine", "Config", "BaseInput.ini")),
                                "bEnableMouseSmoothing=",
                                tooltip_text="Changes how the mouse input is processed. Normally enabled by default")


NoCPK = LWMod("No CPK",
              (path.join(MODS_PATH, "No CPK"), path.join(GAME_DIRECTORY, "Mods")),)

NoStamina = LWMod("No Stamina",
                  None,
                  stamina_off, sprint_delay_off)

CutsceneSkip = LWMod("Cutscene Skip",
                     (path.join(MODS_PATH, "Cutscene Skip"), path.join(GAME_DIRECTORY, "Mods")))

SpeedrunHelper = DisplayMod("Speedrun Helper",
                            (path.join(MODS_PATH, "Speedrun Helper"), path.join(GAME_DIRECTORY, "Mods")),
                            tooltip_text="Speedrun Helper allows you to:\n"
                                         "Set Checkpoints with Ctrl + F1-F4, and TP to them with F1-F4.\n"
                                         "Use the commands Toggle Freecam, TP to Freecam and GodMode.\n"
                                         "You can setup the bindings for Speedrun Helper commands with the launcher.")


CONFIG_FILE = "LauncherConfig.ini"


# Check if it's the first time the Launcher has been launched
def first_launch():
    SpeedrunHelper.install()
    Steam.disable()
    Vsync.disable()
    Borderless.enable()
    bPause.disable()
    with open(CONFIG_FILE, 'w') as f:
        f.write("")


if not os.path.exists(CONFIG_FILE):
    first_launch()

GITHUB_RELEASES_API_URL = "https://api.github.com/repos/HayaiNeko/BetterOutlast2Launcher/releases"
EXECUTABLE_NAME = "BetterOutlast2Launcher.exe"


launcher = Launcher(CURRENT_VERSION)

updater = LauncherUpdater(CURRENT_VERSION, GITHUB_RELEASES_API_URL, EXECUTABLE_NAME)
if launcher.launcher_settings.check_for_updates:
    updater.check_and_update()

updater.do_on_update()


launcher.run()
