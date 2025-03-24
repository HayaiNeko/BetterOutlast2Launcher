import customtkinter as ctk
from ui import fonts, colors  # Provided fonts and colors
from launcher_settings import LauncherSettings
from old_patch import OldPatch

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Launcher Settings")
    root.geometry("600x400")
    root.configure(fg_color=colors["background"])

    # Display launcher settings
    launcher_settings = LauncherSettings()
    launcher_settings.display(root)

    # Create and pack the Manage/Install Old Patch button using the new method
    old_patch_manager = OldPatch()
    old_patch_manager.create_button(root)


    root.mainloop()
