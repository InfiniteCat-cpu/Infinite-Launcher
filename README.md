# Infinite Launcher

A lightweight Windows game launcher built with Python and Tkinter, styled after the
Windows 11 Settings app. Add your favorite games (Minecraft, Roblox, Steam titles,
or any `.exe`) and start them from one clean list.

![Infinite Launcher logo](infinite_logo.png)

## Features

- Windows 11-style UI (light theme, rounded cards, accent colors)
- Auto-detect installed games (Steam, Minecraft, Roblox, and more via the Windows registry)
- Real app icons extracted directly from each game's `.exe`, or set your own custom icon
- Add games manually by picking an `.exe` or entering a launch URI (e.g. `steam://rungameid/...`)
- Start with Windows (optional autostart, launches maximized)
- English and German UI, switchable from the sidebar

## Running from source

Requires Python 3.10+ on Windows.

```bash
pip install -r requirements.txt
python game_launcher.py
```

## Building a standalone .exe

```bash
pyinstaller --noconfirm --onefile --windowed --name "InfiniteLauncher" --icon "infinite_logo.ico" --add-data "infinite_logo.ico;." game_launcher.py
```

The resulting `InfiniteLauncher.exe` is created in `dist/` and needs no Python installation to run.

## Configuration

Settings are stored in your user profile and persist across updates:

- `%USERPROFILE%\game_launcher_config.json` — your game list
- `%USERPROFILE%\game_launcher_settings.json` — UI language
- `%USERPROFILE%\.game_launcher_icons\` — custom icon cache
