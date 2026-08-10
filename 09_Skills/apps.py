import subprocess


def open_app(app_name):
    apps = {
        "safari": "Safari",
        "chrome": "Google Chrome",
        "vscode": "Visual Studio Code",
        "finder": "Finder",
        "terminal": "Terminal",
    }

    app = apps.get(app_name.lower())

    if not app:
        return False

    subprocess.Popen(["open", "-a", app])
    return True

if __name__ == "__main__":
    open_app("Safari")