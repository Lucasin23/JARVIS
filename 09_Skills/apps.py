import subprocess
from pathlib import Path


def get_installed_apps():
    """Find applications installed on the Mac."""

    app_folders = [
        Path("/Applications"),
        Path.home() / "Applications",
        Path("/System/Applications"),
        Path("/System/Applications/Utilities"),
        Path("/System/Library/CoreServices"),
    ]

    apps = {}

    for folder in app_folders:
        if not folder.exists():
            continue

        for app in folder.glob("*.app"):
            name = app.stem
            apps[name.lower()] = name

    return apps

def find_app(app_name):
    """Find an installed app by name."""

    app_name = app_name.lower().strip()

    # Common names people use
    aliases = {
        "vs code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
    }

    app_name = aliases.get(app_name, app_name)

    # Ask macOS to locate the application
    try:
        result = subprocess.run(
            ["mdfind", f'kMDItemKind == "Application" && kMDItemFSName == "{app_name}.app"'],
            capture_output=True,
            text=True
        )

        matches = result.stdout.strip().splitlines()

        if matches:
            return matches[0]

    except Exception:
        pass

    return None

def open_app(app_name):
    """Open an application on the Mac."""

    app_name = app_name.strip()

    aliases = {
        "vs code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
    }

    app_name = aliases.get(app_name.lower(), app_name)

    try:
        subprocess.run(
            ["open", "-a", app_name],
            check=True
        )
        return True

    except subprocess.CalledProcessError:
        return False

def close_app(app_name):
    """Close an application on the Mac."""
    app_name = app_name.strip()

    aliases = {
        "vs code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
    }

    app_name = aliases.get(app_name.lower(), app_name)

    try:
        subprocess.run(
            ["osascript", "-e", f'tell application "{app_name}" to quit'],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False