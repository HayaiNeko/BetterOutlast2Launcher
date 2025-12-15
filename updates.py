import requests
import os
import sys
import subprocess
import textwrap
import configparser
import shutil
from bindings import Binding
from widgets import CustomAskYesNo, CustomShowInfo
from paths import GAME_DIRECTORY, CONFIG_FILE


def version_to_number(version):
    """
    Converts a version string in the format x.y.z into a number 00x00y00z (zero-padded).
    """
    try:
        major, minor, patch = map(int, version.split('.'))
        major_str = f"{major:03d}"
        minor_str = f"{minor:03d}"
        patch_str = f"{patch:03d}"
        version_number = int(major_str + minor_str + patch_str)
        return version_number
    except ValueError:
        raise ValueError("Invalid version format. Expected format 'x.y.z'")

class LauncherUpdater:
    def __init__(self, current_version, github_releases_api_url, executable_name):
        self.current_version = current_version
        self.github_releases_api_url = github_releases_api_url
        self.executable_name = executable_name
        self.config_file = CONFIG_FILE
        self.objects = {}

        self._load_old_version()

    def register(self, name, obj):
        """
        Registers an object in the updater's context so it can be accessed during update operations.
        """
        self.objects[name] = obj

    def get(self, name):
        """
        Retrieves an object from the registry, or None if it doesn't exist.
        """
        return self.objects.get(name)

    def _load_old_version(self) -> None:
        """
        Populate self.old_version with the value stored under
        [Update] version in the config file.  Leaves it to None if the
        file/section/key doesn't exist.
        """
        config = configparser.ConfigParser()

        if not os.path.exists(self.config_file):
            self.old_version = None  # fichier absent
            return

        config.read(self.config_file)
        self.old_version = config.get("Update", "version", fallback=None)

    def get_latest_release(self):
        """
        Fetches the latest release from GitHub and returns the tag and download URL
        for the executable asset.
        """
        try:
            response = requests.get(self.github_releases_api_url)
            response.raise_for_status()
            releases = response.json()

            if not releases:
                print("No releases found.")
                return None, None

            latest_release = releases[0]
            tag_name = latest_release["tag_name"]

            for asset in latest_release.get("assets", []):
                if asset["name"] == self.executable_name:
                    return tag_name, asset["browser_download_url"]

            print(f"Executable {self.executable_name} not found in the latest release.")
            return None, None
        except requests.RequestException as e:
            print(f"Error fetching release information: {e}")
            return None, None

    def is_update_required(self, latest_version):
        """
        Compares the current version with the latest version using numeric conversion.
        """
        print(f"Current version: {self.current_version}")
        print(f"Latest version: {latest_version}")
        try:
            current_num = version_to_number(self.current_version)
            latest_num = version_to_number(latest_version)
            return current_num != latest_num
        except ValueError as e:
            print(f"Error comparing versions: {e}")
            return False

    def download_executable(self, download_url, output_path):
        """
        Downloads the executable from the provided URL and saves it to output_path.
        """
        try:
            print(f"Downloading {self.executable_name}...")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"{self.executable_name} downloaded successfully as {output_path}.")
            return True
        except requests.RequestException as e:
            print(f"Error downloading the executable: {e}")
            return False

    def update_config_version(self, version):
        """
        Writes the downloaded version to the configuration file under the "Update" section.
        """
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        if "Update" not in config:
            config["Update"] = {}
        config["Update"]["version"] = version
        with open(self.config_file, "w") as configfile:
            config.write(configfile)
        print(f"Config file updated: [Update] version = {version}")

    @staticmethod
    def replace(temp_executable_path, current_executable_path):
        """
        Creates and executes a batch script that waits for the current launcher process to exit,
        replaces the old executable with the new one.
        """
        try:
            batch_script = f"""@echo off
            :check_file
            if exist "{temp_executable_path}" (
                timeout /t 1 >nul
                move /y "{temp_executable_path}" "{current_executable_path}"
            ) else (
                goto end
            )
            goto check_file

            :end
            del "%~f0"
            exit
            """

            batch_file = "update_launcher.bat"

            # Write the batch script to a file
            with open(batch_file, "w") as file:
                file.write(batch_script)

            # Run the batch file
            subprocess.Popen([batch_file], shell=True)
            print("Update batch script started.")
            sys.exit(0)  # Exit the current program
        except Exception as e:
            print(f"Error during replacement: {e}")

    def prompt_user_for_update(self, tag_name, download_url, current_executable_path):
        """
        Prompts the user with a CustomTkinter modal yes/no dialog to confirm the update.
        If confirmed, downloads the new executable, updates the config file with the new version,
        and initiates the replacement process.
        """
        user_response = CustomAskYesNo.askyesno(
            "Update Available",
            f"A new version ({tag_name}) is available.\nDo you want to update?"
        )

        if user_response:
            temp_executable_path = os.path.join(os.getcwd(), "temp_" + self.executable_name)
            if self.download_executable(download_url, temp_executable_path):
                # Update the config file with the new version
                self.replace(temp_executable_path, current_executable_path)
                return "updated"
            else:
                print("Failed to download the update.")
                return "failed"
        else:
            return "skipped"

    def check_and_update(self):
        """
        Main function to check for updates and initiate the update process if required.
        """
        current_executable_path = sys.argv[0]
        print("Checking for updates...")
        tag_name, download_url = self.get_latest_release()

        if not tag_name or not download_url:
            print("No updates available or error fetching release.")
            return "no_update"

        if not self.is_update_required(tag_name):
            print("The launcher is already up-to-date.")
            return "no_update"

        return self.prompt_user_for_update(tag_name, download_url, current_executable_path)

    def updated(self):
        """
        Checks the configuration file to verify if the launcher version has changed.
        Returns True if the version in the config file differs from the current version.
        """
        if self.old_version is None:
            return False

        if self.old_version != self.current_version:
            print("Launcher version has been updated according to the config file.")
            return True
        return False

    def _get_release_notes(self, tag_name: str) -> str:
        """
        Returns the release‑notes body for the given tag
        (empty string on failure).
        """
        url = f"{self.github_releases_api_url}/tags/{tag_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json().get("body", "")
        except requests.RequestException:
            return ""

    def show_changelog(self, tag_name: str):
        """
        Fetches release notes for *tag_name* and displays them
        in a scrollable information dialog.
        """
        notes = self._get_release_notes(tag_name)
        if not notes:
            notes = "No changelog available for this release."

        # Optional: ensure CRLF or at least LF line breaks for neat display
        formatted_notes = textwrap.dedent(notes).strip()

        CustomShowInfo.showinfo(
            title=f"Changelog — {tag_name}",
            message=formatted_notes
        )

    def do_on_update(self):
        if self.updated():
            self.show_changelog(self.current_version)

            if version_to_number(self.old_version) < version_to_number("1.1.0"):
                mods_dir = os.path.join(GAME_DIRECTORY, "Mods")
                for entry in os.listdir(mods_dir):
                    full_path = os.path.join(mods_dir, entry)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                        print(f"Deleted : {full_path}")

            if version_to_number(self.old_version) < version_to_number("1.1.3"):
                Binding.file.replace_term("OL_USE", "OLA_USE")
                Binding.file.delete_duplicates("setbind LeftMouseButton OLA_USE | setbind")
                Binding.file.write_lines()

                Binding.file.replace_term("ToggleGodMode", "GodMode")
                Binding.file.replace_term("ToggleFreeCam", "FreeCam")
                Binding.file.write_lines()

            if version_to_number(self.old_version) < version_to_number("1.3.0"):
                Binding.file.remove_line("DisplayAll OLHero Location")
                Binding.file.remove_line("DisplayALL OLHero Velocity")
                Binding.file.write_lines()

            if version_to_number(self.old_version) < version_to_number("1.3.4"):
                SpeedrunHelper = self.get("SpeedrunHelper")
                SpeedrunHelper.uninstall()
                SpeedrunHelper.install()

        self.update_config_version(self.current_version)
