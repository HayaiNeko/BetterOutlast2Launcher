SHELL := powershell
.SHELLFLAGS := -NoProfile -ExecutionPolicy Bypass -Command

PYINSTALLER := pyinstaller
NAME := BetterOutlast2Launcher
ICON := OutlastII_icon.png
MODS_DIR := Mods
MODS_ZIP := Mods.zip
SRC := main.py
DIST_DIR := dist
BUILD_DIR := build

.PHONY: all build build-console clean zipmods help
all: build

zipmods:
	if (Test-Path '$(MODS_ZIP)') { Remove-Item -Force '$(MODS_ZIP)' }
	Push-Location '$(MODS_DIR)'; Compress-Archive -Path * -DestinationPath '..\$(MODS_ZIP)' -Force; Pop-Location
	@echo "✅ Mods.zip created successfully!"

build: zipmods
	$(PYINSTALLER) --onefile --name $(NAME) --icon=$(ICON) --add-data "$(MODS_ZIP);." --add-data "$(ICON);." $(SRC) --noconsole
	@echo "✅ Build: $(DIST_DIR)/$(NAME).exe"

build-console: zipmods
	$(PYINSTALLER) --onefile --name $(NAME)_console --icon=$(ICON) --add-data "$(MODS_ZIP);." --add-data "$(ICON);." $(SRC)
	@echo "✅ Build: $(DIST_DIR)/$(NAME)_console.exe"

clean:
	if (Test-Path '$(BUILD_DIR)') { Remove-Item -Recurse -Force '$(BUILD_DIR)' }
	if (Test-Path '$(DIST_DIR)') { Remove-Item -Recurse -Force '$(DIST_DIR)' }
	if (Test-Path '$(NAME).spec') { Remove-Item -Force '$(NAME).spec' }
	if (Test-Path '$(NAME)_console.spec') { Remove-Item -Force '$(NAME)_console.spec' }
	if (Test-Path '$(MODS_ZIP)') { Remove-Item -Force '$(MODS_ZIP)' }

help:
	@echo "make, make build, make build-console, make clean"
