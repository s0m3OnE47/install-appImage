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

## Putting `install-appimage` on your PATH

Clone or unpack this repo, then either:

- **Recommended (works with `sudo`):** install into `/usr/local/bin`, which is part of sudo’s default `secure_path`:

  ```bash
  cd /path/to/install-appImage
  sudo make install
  ```

  After that, `sudo install-appimage …` resolves the command normally.

- **Ad hoc:** run it by absolute path, or from the repo:

  ```bash
  sudo ./install-appimage ~/Downloads/App.AppImage --name MyApp
  ```

### Why `sudo install-appimage` says “command not found”

`sudo` does not use your interactive shell `$PATH`; it uses a fixed list (often `/usr/local/bin`, `/usr/bin`, …). If `install-appimage` lives only in e.g. `~/.local/bin`, sudo will not find it.

Until you run `sudo make install`, you can still invoke the script explicitly:

```bash
sudo "$(command -v install-appimage)" ~/Downloads/App.AppImage --name MyApp
```

Your shell resolves `command -v` **before** sudo runs, so sudo executes the full path.

## Usage

```bash
sudo install-appimage <path-to-appimage> [--name <app-name>] [--sandbox]

sudo install-appimage --uninstall <app-name>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<path-to-appimage>` | Yes* | Path to the `.AppImage` file to install |
| `--name <app-name>` | No | Name for the application. If omitted, a dialog box will prompt for it. |
| `--sandbox` | No | Omit `--no-sandbox` from the `.desktop` launcher `Exec` line (default adds it). |
| `--uninstall <app-name>` | No** | Remove `/opt/<app-name>/`, `/usr/share/applications/<app-name>.desktop`, and the matching `PATH` line in `~/.zshrc` if present. |

\* Required for install; omit when using `--uninstall`.

\*\* Mutually exclusive with the AppImage path and with `--name` / `--sandbox`.

### Examples

Install with an explicit name:

```bash
sudo install-appimage ~/Downloads/Obsidian.AppImage --name Obsidian
```

Install without a name (a dialog will ask for it):

```bash
sudo install-appimage ~/Downloads/SomeApp.AppImage
```

Uninstall an app previously installed as `Obsidian`:

```bash
sudo install-appimage --uninstall Obsidian
```

## What Gets Created

Given `--name MyApp`:

```
/opt/MyApp/
├── MyApp               # executable AppImage (no .AppImage suffix)
└── MyApp.png           # icon (extension matches the file you selected)

/usr/share/applications/MyApp.desktop   # desktop entry
```

The `.desktop` file contents:

```ini
[Desktop Entry]
Type=Application
Name=MyApp
Exec=/opt/MyApp/MyApp --no-sandbox
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
