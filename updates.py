import requests
import os
import sys
import subprocess
import textwrap
import configparser
from widgets import CustomAskYesNo


class LauncherUpdater:
    def __init__(self, current_version, github_releases_api_url, executable_name, config_file="LauncherConfig.ini"):
        self.current_version = current_version
        self.github_releases_api_url = github_releases_api_url
        self.executable_name = executable_name
        self.config_file = config_file

    @staticmethod
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
            current_num = LauncherUpdater.version_to_number(self.current_version)
            latest_num = LauncherUpdater.version_to_number(latest_version)
            return current_num < latest_num
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
    def replace_and_restart(temp_executable_path, current_executable_path):
        """
        Creates and executes a batch script that waits for the current launcher process to exit,
        replaces the old executable with the new one, and restarts the launcher.
        """
        try:
            # Create a batch file that takes two parameters:
            # %1 - path to the temporary downloaded executable
            # %2 - path to the current executable to be replaced and relaunched
            batch_script = textwrap.dedent(r'''@echo off
            set "temp_exe=%~1"
            set "current_exe=%~2"

            :waitloop
            timeout /t 1 >nul
            tasklist /fi "imagename eq %~nx2" | findstr /i "%~nx2" >nul
            if %ERRORLEVEL%==0 goto waitloop

            move /y "%temp_exe%" "%current_exe%"
            del "%~f0"
            ''')
            batch_file = "update_launcher.bat"
            with open(batch_file, "w") as file:
                file.write(batch_script)

            # Launch the batch script with the temporary and current executable paths as arguments
            subprocess.Popen([batch_file, temp_executable_path, current_executable_path], shell=True)
            print("Update batch script launched.")
            sys.exit(0)
        except Exception as e:
            print(f"Error during replacement and restart: {e}")

    def prompt_user_for_update(self, tag_name, download_url, current_executable_path):
        """
        Prompts the user with a CustomTkinter modal yes/no dialog to confirm the update.
        If confirmed, downloads the new executable, updates the config file with the new version,
        and initiates the replacement/restart process.
        """
        user_response = CustomAskYesNo.askyesno(
            "Update Available",
            f"A new version ({tag_name}) is available.\nDo you want to update?"
        )

        if user_response:
            temp_executable_path = os.path.join(os.getcwd(), "temp_" + self.executable_name)
            if self.download_executable(download_url, temp_executable_path):
                # Update the config file with the new version
                self.replace_and_restart(temp_executable_path, current_executable_path)
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
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            return False

        config.read(self.config_file)
        if "Update" in config and "version" in config["Update"]:
            config_version = config["Update"]["version"]
            if config_version != self.current_version:
                print("Launcher version has been updated according to the config file.")
                return True
        return False

    def do_on_update(self):
        if self.updated():
            pass

        self.update_config_version(self.current_version)
