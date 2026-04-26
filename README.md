# install-appimage

A Python script that installs AppImage files as proper desktop applications on Linux.

## What It Does

1. Copies the AppImage into `/opt/<name>/` and makes it executable.
2. Opens a GUI dialog (Zenity) to pick an icon, then copies it alongside the AppImage.
3. Creates a `.desktop` file in `/usr/share/applications/` so the app appears in your launcher.
4. Sets ownership of `/opt/<name>/` to the invoking user (not root).
5. Adds `/opt/<name>/` to `$PATH` in `~/.zshrc` (only if not already present).

## Prerequisites

- **Python 3** (uses only the standard library)
- **Zenity** — install with `sudo apt install zenity` if not already present
- **zsh** — the script appends to `~/.zshrc`

## Usage

```bash
sudo python3 install-appimage.py <path-to-appimage> [--name <app-name>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<path-to-appimage>` | Yes | Path to the `.AppImage` file to install |
| `--name <app-name>` | No | Name for the application. If omitted, a dialog box will prompt for it. |

### Examples

Install with an explicit name:

```bash
sudo python3 install-appimage.py ~/Downloads/Obsidian.AppImage --name Obsidian
```

Install without a name (a dialog will ask for it):

```bash
sudo python3 install-appimage.py ~/Downloads/SomeApp.AppImage
```

## What Gets Created

Given `--name MyApp`:

```
/opt/MyApp/
├── MyApp.AppImage      # executable AppImage
└── MyApp.png           # icon (extension matches the file you selected)

/usr/share/applications/MyApp.desktop   # desktop entry
```

The `.desktop` file contents:

```ini
[Desktop Entry]
Type=Application
Name=MyApp
Exec=/opt/MyApp/MyApp.AppImage --no-sandbox
Icon=/opt/MyApp/MyApp.png
Terminal=false
StartupWMClass=myapp
Categories=Utility;
```

## Notes

- The script must be run with `sudo` since it writes to `/opt/` and `/usr/share/applications/`.
- Ownership of the installed directory is set to the invoking user (resolved via `$SUDO_USER`), not root.
- The `$PATH` export is appended to the real user's `~/.zshrc`, not root's. Run `source ~/.zshrc` or open a new terminal to pick up the change.
- The AppImage is launched with `--no-sandbox` by default.
