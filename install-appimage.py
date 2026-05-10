#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_root():
    if os.geteuid() != 0:
        sys.exit("Error: This script must be run as root (use sudo).")


def check_zenity():
    if shutil.which("zenity") is None:
        sys.exit("Error: Zenity is not installed. Install it with: sudo apt install zenity")


def zenity_entry(prompt):
    try:
        result = subprocess.run(
            ["zenity", "--entry", "--title=AppImage Installer", f"--text={prompt}"],
            capture_output=True, text=True, check=True,
        )
        name = result.stdout.strip()
        if not name:
            sys.exit("Error: No application name provided.")
        return name
    except subprocess.CalledProcessError:
        sys.exit("Cancelled by user.")


def zenity_file_selection():
    try:
        result = subprocess.run(
            [
                "zenity", "--file-selection",
                "--title=Select an icon for the application",
                "--file-filter=Image files | *.png *.svg *.xpm *.ico",
            ],
            capture_output=True, text=True, check=True,
        )
        path = result.stdout.strip()
        if not path:
            sys.exit("Error: No icon selected.")
        return Path(path)
    except subprocess.CalledProcessError:
        sys.exit("Cancelled by user.")


def get_real_user():
    return os.environ.get("SUDO_USER", os.getlogin())


def get_real_user_home():
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        return Path(f"/home/{sudo_user}")
    return Path.home()


def chown_recursive(path: Path, user: str):
    shutil.chown(path, user=user, group=user)
    if path.is_dir():
        for child in path.rglob("*"):
            shutil.chown(child, user=user, group=user)


def update_zsh_path(app_dir: Path):
    zshrc = get_real_user_home() / ".zshrc"
    export_line = f'export PATH="{app_dir}:$PATH"'

    if zshrc.exists():
        content = zshrc.read_text()
        if export_line in content:
            return
    else:
        content = ""

    with open(zshrc, "a") as f:
        f.write(f"\n{export_line}\n")
    print(f"Added {app_dir} to $PATH in {zshrc}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Install a Linux AppImage under /opt/<name>, add a .desktop launcher, "
            "and append the app directory to the real user's ~/.zshrc PATH. "
            "Must be run with sudo; uses Zenity dialogs for the app name (if not given) "
            "and for choosing an icon image."
        ),
        epilog=(
            "Usage flow:\n"
            "  1. sudo python3 install-appimage.py /path/to/app.AppImage\n"
            "  2. If --name is omitted, enter the display name in the dialog.\n"
            "  3. Pick a PNG, SVG, XPM, or ICO file for the launcher icon.\n"
            "  4. The AppImage is copied to /opt/<name>/, owned by the user who invoked sudo.\n"
            "\n"
            "Requires: root, Zenity (e.g. apt install zenity), and a graphical session for dialogs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("appimage", help="Path to the .AppImage file to install")
    parser.add_argument(
        "--name",
        metavar="NAME",
        help="Application name and install folder under /opt (Zenity prompt if omitted)",
    )
    args = parser.parse_args()

    check_root()
    check_zenity()

    appimage_path = Path(args.appimage).resolve()
    if not appimage_path.is_file():
        sys.exit(f"Error: '{appimage_path}' is not a valid file.")

    name = args.name if args.name else zenity_entry("Enter a name for the application:")

    app_dir = Path(f"/opt/{name}")
    app_dir.mkdir(parents=True, exist_ok=True)

    dest_appimage = app_dir / f"{name}.AppImage"
    shutil.copy2(appimage_path, dest_appimage)
    dest_appimage.chmod(0o755)
    print(f"Installed AppImage to {dest_appimage}")

    icon_src = zenity_file_selection()
    icon_dest = app_dir / f"{name}{icon_src.suffix}"
    shutil.copy2(icon_src, icon_dest)
    print(f"Icon copied to {icon_dest}")

    real_user = get_real_user()
    chown_recursive(app_dir, real_user)
    print(f"Ownership set to {real_user} for {app_dir}")

    desktop_entry = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={name}\n"
        f"Exec={dest_appimage} --no-sandbox\n"
        f"Icon={icon_dest}\n"
        "Terminal=false\n"
        f"StartupWMClass={name.lower()}\n"
        "Categories=Utility;\n"
    )
    desktop_path = Path(f"/usr/share/applications/{name}.desktop")
    desktop_path.write_text(desktop_entry)
    print(f"Created desktop entry at {desktop_path}")

    update_zsh_path(app_dir)

    print(f"\n'{name}' installed successfully.")


if __name__ == "__main__":
    main()
