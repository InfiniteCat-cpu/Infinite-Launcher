import ctypes
import json
import os
import subprocess
import sys
import uuid
import winreg
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from PIL import Image, ImageTk

try:
    import win32gui
    import win32ui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# Make the process DPI-aware so text and shapes render crisp instead of
# being blurrily upscaled by Windows on high-DPI screens.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

CONFIG_FILE = os.path.join(os.path.expanduser("~"), "game_launcher_config.json")
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), "game_launcher_settings.json")
ICON_DIR = os.path.join(os.path.expanduser("~"), ".game_launcher_icons")
os.makedirs(ICON_DIR, exist_ok=True)


def resource_path(filename):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


APP_ICON_PATH = resource_path("infinite_logo.ico")

FONT_FAMILY = "Segoe UI"

# Windows 11 (light) Settings-style palette
BG_PAGE = "#f3f3f3"
BG_SIDEBAR = "#f9f9f9"
BG_CARD = "#ffffff"
BORDER = "#e5e5e5"
ACCENT = "#0067C0"
ACCENT_HOVER = "#1975D1"
ACCENT_LIGHT = "#e8f1fb"
TEXT_PRIMARY = "#1b1b1b"
TEXT_SECONDARY = "#5d5d5d"

AVATAR_COLORS = ["#0067C0", "#7719AA", "#C239B3", "#EA005E",
                 "#E81123", "#EA6A00", "#10893E", "#00B7C3"]

DEFAULT_GAMES = [
    {"name": "Minecraft", "target": "minecraft://"},
    {"name": "Roblox", "target": "roblox://"},
]

IGNORE_KEYWORDS = [
    "redistributable", "runtime", "update for", "security update", "hotfix",
    "driver", "framework", "visual c++", ".net ", "directx", "webview",
    "sdk", "kb2", "kb3", "kb4", "kb5", "language pack", "uninstall",
]


def load_games():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    save_games(DEFAULT_GAMES)
    return list(DEFAULT_GAMES)


def save_games(games):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------

LANGUAGES = [
    ("en", "English"),
    ("de", "Deutsch"),
]
DEFAULT_LANGUAGE = "en"

TRANSLATIONS = {
    "nav_home": {"de": "🏠 Meine Spiele", "en": "🏠 My Games"},
    "nav_scan": {"de": "🔍 Automatisch suchen", "en": "🔍 Auto-detect"},
    "nav_add": {"de": "➕ Spiel hinzufügen", "en": "➕ Add Game"},
    "nav_remove": {"de": "🗑 Spiel entfernen", "en": "🗑 Remove Game"},
    "nav_autostart": {"de": "🚀 Mit Windows starten", "en": "🚀 Start with Windows"},
    "nav_languages": {"de": "🌐 Sprachen", "en": "🌐 Languages"},
    "lang_dialog_title": {"de": "Sprache wählen", "en": "Choose Language"},
    "lang_dialog_header": {"de": "Sprache", "en": "Language"},
    "header_title": {"de": "Meine Spiele", "en": "My Games"},
    "header_subtitle": {
        "de": "Wähle ein Spiel zum Starten, oder füge eines hinzu.",
        "en": "Choose a game to launch, or add a new one.",
    },
    "btn_start": {"de": "Starten", "en": "Launch"},
    "empty_state": {"de": "Noch keine Spiele hinzugefügt.", "en": "No games added yet."},
    "err_start_title": {"de": "Fehler beim Starten", "en": "Launch Failed"},
    "err_start_msg": {
        "de": "'{name}' konnte nicht gestartet werden:\n{exc}\n\nZiel: {target}",
        "en": "'{name}' could not be started:\n{exc}\n\nTarget: {target}",
    },
    "add_title": {"de": "Spiel hinzufügen", "en": "Add Game"},
    "add_name_prompt": {"de": "Name des Spiels:", "en": "Game name:"},
    "add_choice_title": {"de": "Ziel wählen", "en": "Choose Target"},
    "add_choice_msg": {
        "de": "Möchtest du eine .exe-Datei auswählen?\n\n"
              "Ja = Datei auswählen\nNein = Link/URI manuell eingeben (z.B. steam://rungameid/12345)",
        "en": "Do you want to select an .exe file?\n\n"
              "Yes = pick a file\nNo = enter a link/URI manually (e.g. steam://rungameid/12345)",
    },
    "filedialog_exe_title": {"de": "Spiel-Programm auswählen", "en": "Select Game Program"},
    "filetype_programs": {"de": "Programme", "en": "Programs"},
    "filetype_all": {"de": "Alle Dateien", "en": "All Files"},
    "add_link_title": {"de": "Link/URI eingeben", "en": "Enter Link/URI"},
    "add_link_prompt": {"de": "Link oder Pfad eingeben:", "en": "Enter a link or path:"},
    "info_title": {"de": "Info", "en": "Info"},
    "remove_none_msg": {"de": "Keine Spiele vorhanden.", "en": "No games available."},
    "remove_title": {"de": "Spiel entfernen", "en": "Remove Game"},
    "remove_btn": {"de": "Entfernen", "en": "Remove"},
    "remove_none_selected_title": {"de": "Kein Spiel ausgewählt", "en": "No Game Selected"},
    "remove_none_selected_msg": {
        "de": "Bitte zuerst ein Spiel in der Liste anklicken, dann auf 'Entfernen' klicken.",
        "en": "Please click a game in the list first, then click 'Remove'.",
    },
    "remove_done_title": {"de": "Entfernt", "en": "Removed"},
    "remove_done_msg": {"de": "'{name}' wurde entfernt.", "en": "'{name}' was removed."},
    "icon_change_title": {"de": "Icon ändern", "en": "Change Icon"},
    "icon_change_msg": {
        "de": "Neues Icon für '{name}':\n\n"
              "Ja = Bilddatei auswählen\nNein = Icon aus einer .exe-Datei holen\nAbbrechen = nichts ändern",
        "en": "New icon for '{name}':\n\n"
              "Yes = pick an image file\nNo = extract icon from an .exe file\nCancel = keep current icon",
    },
    "filedialog_image_title": {"de": "Bild auswählen", "en": "Select Image"},
    "filetype_images": {"de": "Bilder", "en": "Images"},
    "err_title": {"de": "Fehler", "en": "Error"},
    "err_image_load_msg": {
        "de": "Bild konnte nicht geladen werden:\n{exc}",
        "en": "Could not load image:\n{exc}",
    },
    "filedialog_icon_exe_title": {"de": "Programm für Icon auswählen", "en": "Select Program for Icon"},
    "err_no_icon_msg": {
        "de": "Aus dieser Datei konnte kein Icon gelesen werden.",
        "en": "No icon could be read from this file.",
    },
    "scan_title": {"de": "Installierte Spiele suchen", "en": "Search for Installed Games"},
    "scan_header": {"de": "Gefundene Programme", "en": "Found Programs"},
    "scan_searching": {"de": "Suche läuft...", "en": "Searching..."},
    "scan_found": {"de": "{n} Programme gefunden", "en": "{n} programs found"},
    "scan_none": {"de": "Nichts gefunden", "en": "Nothing found"},
    "scan_add_btn": {"de": "Ausgewählte hinzufügen", "en": "Add Selected"},
    "scan_done_title": {"de": "Fertig", "en": "Done"},
    "scan_done_msg": {"de": "{n} Spiel(e) hinzugefügt.", "en": "{n} game(s) added."},
    "autostart_err_msg": {
        "de": "Autostart konnte nicht geändert werden:\n{exc}",
        "en": "Could not change autostart:\n{exc}",
    },
    "autostart_on_title": {"de": "Autostart aktiviert", "en": "Autostart Enabled"},
    "autostart_on_msg": {
        "de": "Der Infinite Launcher startet jetzt automatisch (maximiert), "
              "wenn du dich bei Windows anmeldest.",
        "en": "Infinite Launcher will now start automatically (maximized) "
              "when you sign in to Windows.",
    },
    "autostart_off_title": {"de": "Autostart deaktiviert", "en": "Autostart Disabled"},
    "autostart_off_msg": {
        "de": "Der automatische Start wurde deaktiviert.",
        "en": "Automatic startup has been disabled.",
    },
}


def avatar_color(name):
    return AVATAR_COLORS[sum(map(ord, name)) % len(AVATAR_COLORS)]


# ---------------------------------------------------------------------------
# Start with Windows
# ---------------------------------------------------------------------------

AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_NAME = "InfiniteLauncher"


def get_launch_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    return f'"{sys.executable}" "{os.path.abspath(__file__)}"'


def is_autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY) as key:
            winreg.QueryValueEx(key, AUTOSTART_NAME)
            return True
    except OSError:
        return False


def set_autostart(enabled):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, get_launch_command())
        else:
            try:
                winreg.DeleteValue(key, AUTOSTART_NAME)
            except FileNotFoundError:
                pass


# ---------------------------------------------------------------------------
# Icon handling
# ---------------------------------------------------------------------------

def extract_exe_icon(path, size=64):
    """Pull the real app icon out of an .exe file, at high resolution."""
    if not HAS_WIN32 or not path or not os.path.isfile(path):
        return None
    large = small = None
    try:
        large, small = win32gui.ExtractIconEx(path, 0, 1)
        hicon = (large or small or [None])[0]
        if not hicon:
            return None
        info = win32gui.GetIconInfo(hicon)
        hbm_color = info[4]
        bmp = win32ui.CreateBitmapFromHandle(hbm_color)
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGBA", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr, "raw", "BGRA", 0, 1
        )
        if img.getextrema()[3] == (0, 0):
            img.putalpha(255)
        try:
            win32gui.DeleteObject(hbm_color)
            win32gui.DeleteObject(info[3])
        except Exception:
            pass
        return img.resize((size, size), Image.LANCZOS)
    except Exception:
        return None
    finally:
        for handles in (large, small):
            for h in handles or []:
                try:
                    win32gui.DestroyIcon(h)
                except Exception:
                    pass


def to_square(img):
    w, h = img.size
    if w == h:
        return img
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return img.crop((left, top, left + s, top + s))


def square_icon(img):
    return to_square(img.convert("RGBA"))


def store_custom_icon(img):
    """Save a high-res, square copy to the icon cache and return its path."""
    img = to_square(img.convert("RGBA")).resize((128, 128), Image.LANCZOS)
    path = os.path.join(ICON_DIR, f"{uuid.uuid4().hex}.png")
    img.save(path, "PNG")
    return path


# ---------------------------------------------------------------------------
# Auto-detection of installed games
# ---------------------------------------------------------------------------

def _scan_uninstall_keys():
    found = []
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, path in roots:
        try:
            key = winreg.OpenKey(hive, path)
        except OSError:
            continue
        with key:
            count = winreg.QueryInfoKey(key)[0]
            for i in range(count):
                try:
                    sub_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub_name) as sub:
                        name = winreg.QueryValueEx(sub, "DisplayName")[0]
                        if any(k in name.lower() for k in IGNORE_KEYWORDS):
                            continue
                        exe_path = None
                        try:
                            icon = winreg.QueryValueEx(sub, "DisplayIcon")[0]
                            candidate = icon.split(",")[0].strip('"')
                            if candidate.lower().endswith(".exe") and os.path.isfile(candidate):
                                exe_path = candidate
                        except (FileNotFoundError, OSError):
                            pass
                        if exe_path:
                            found.append({"name": name, "target": exe_path})
                except OSError:
                    continue
    return found


def _scan_known_games():
    found = []

    roblox_versions = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "Versions")
    if os.path.isdir(roblox_versions):
        for v in os.listdir(roblox_versions):
            exe = os.path.join(roblox_versions, v, "RobloxPlayerBeta.exe")
            if os.path.isfile(exe):
                found.append({"name": "Roblox", "target": exe})
                break

    for p in (r"C:\Program Files (x86)\Minecraft Launcher\MinecraftLauncher.exe",
              r"C:\Program Files\Minecraft Launcher\MinecraftLauncher.exe"):
        if os.path.isfile(p):
            found.append({"name": "Minecraft Launcher", "target": p})
            break

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-AppxPackage -Name *Minecraft*).PackageFamilyName"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if line:
                found.append({
                    "name": "Minecraft (Microsoft Store)",
                    "target": f"shell:AppsFolder\\{line}!App",
                })
                break
    except Exception:
        pass

    steam_exe = None
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, r"SOFTWARE\Valve\Steam") as k:
                steam_exe = winreg.QueryValueEx(k, "SteamExe")[0]
                break
        except OSError:
            continue
    if steam_exe and os.path.isfile(steam_exe):
        found.append({"name": "Steam", "target": steam_exe})

    return found


def scan_installed_games():
    results = _scan_known_games() + _scan_uninstall_keys()
    seen = set()
    deduped = []
    for g in results:
        key = g["name"].strip().lower()
        if key in seen or not key:
            continue
        seen.add(key)
        deduped.append(g)
    deduped.sort(key=lambda g: g["name"].lower())
    return deduped


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def rounded_points(w, h, r):
    r = min(r, w / 2, h / 2)
    return [r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h,
            w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0]


def translate_points(points, dx, dy):
    return [v + dx if i % 2 == 0 else v + dy for i, v in enumerate(points)]


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=140, height=36, radius=18,
                 bg=BG_PAGE, fill=ACCENT, hover=ACCENT_HOVER, fg="#ffffff",
                 font=(FONT_FAMILY, 10), icon=None):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.fill = fill
        self.hover = hover
        self.w, self.h, self.r = width, height, radius
        self.rect = self.create_polygon(rounded_points(width, height, radius),
                                         smooth=True, fill=fill, outline=fill)
        if icon == "pencil":
            self._draw_pencil(width / 2, height / 2, min(width, height) * 0.6, fg)
        elif text:
            self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill=self.hover, outline=self.hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=self.fill, outline=self.fill))
        self.config(cursor="hand2")

    def _draw_pencil(self, cx, cy, size, color):
        s = size
        self.create_line(cx - s * 0.32, cy + s * 0.32, cx + s * 0.30, cy - s * 0.30,
                          width=max(2, s * 0.2), fill=color, capstyle="round")
        self.create_polygon(
            cx - s * 0.44, cy + s * 0.44,
            cx - s * 0.24, cy + s * 0.44,
            cx - s * 0.24, cy + s * 0.24,
            fill=color, outline=color
        )


class RoundedCard(tk.Frame):
    """A white, rounded-corner container (with a soft drop shadow) that
    hosts an inner content frame."""

    SHADOW_DX, SHADOW_DY = 3, 4

    def __init__(self, parent, bg=BG_PAGE, radius=10, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.radius = radius
        self.inner = tk.Frame(self.canvas, bg=BG_CARD)
        self.win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.rect = None
        self.shadow = None
        self.inner.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        w = self.inner.winfo_reqwidth()
        h = self.inner.winfo_reqheight()
        self.canvas.config(width=w + self.SHADOW_DX + 1, height=h + self.SHADOW_DY + 1)
        self.canvas.coords(self.win, 0, 0)
        if self.rect:
            self.canvas.delete(self.rect)
        if self.shadow:
            self.canvas.delete(self.shadow)
        shadow_pts = translate_points(rounded_points(w, h, self.radius), self.SHADOW_DX, self.SHADOW_DY)
        self.shadow = self.canvas.create_polygon(shadow_pts, smooth=True, fill="#dcdcdc", outline="")
        self.rect = self.canvas.create_polygon(
            rounded_points(w, h, self.radius), smooth=True,
            fill=BG_CARD, outline=BORDER
        )
        self.canvas.tag_lower(self.rect)
        self.canvas.tag_lower(self.shadow)


def avatar(parent, name, size=44):
    c = tk.Canvas(parent, width=size, height=size, bg=BG_CARD, highlightthickness=0)
    c.create_oval(2, 2, size - 2, size - 2, fill=avatar_color(name), outline="")
    c.create_text(size / 2, size / 2, text=name[:1].upper(),
                   fill="#ffffff", font=(FONT_FAMILY, 14, "bold"))
    return c


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Infinite Launcher")
        if os.path.isfile(APP_ICON_PATH):
            try:
                self.root.iconbitmap(APP_ICON_PATH)
            except Exception:
                pass
        self.root.geometry("800x680")
        self.root.minsize(700, 480)
        self.root.configure(bg=BG_PAGE)

        self.games = load_games()
        self.icon_cache = {}
        self.icon_photos = []
        self.autostart_row = None
        self.lang = load_settings().get("language", DEFAULT_LANGUAGE)

        self._build_layout()
        self.render_games()

        self.root.state("zoomed")

    def t(self, key, **kwargs):
        text = TRANSLATIONS[key][self.lang]
        return text.format(**kwargs) if kwargs else text

    def _new_dialog(self, title, geometry):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(geometry)
        win.configure(bg=BG_PAGE)
        if os.path.isfile(APP_ICON_PATH):
            try:
                win.iconbitmap(APP_ICON_PATH)
            except Exception:
                pass
        return win

    def set_language(self, code):
        if code == self.lang:
            return
        self.lang = code
        save_settings({"language": self.lang})
        # Defer the rebuild so the click event that triggered this finishes
        # unwinding first — destroying the widget tree synchronously from
        # inside its own event handler can crash Tk.
        self.root.after(10, self.rebuild_ui)

    def language_dialog(self):
        win = self._new_dialog(self.t("lang_dialog_title"), "300x320")

        tk.Label(win, text=self.t("lang_dialog_header"), bg=BG_PAGE, fg=TEXT_PRIMARY,
                 font=(FONT_FAMILY, 13, "bold")).pack(anchor="w", padx=18, pady=(18, 8))

        def pick(code):
            # Defer past this click event before we tear the dialog down.
            self.root.after(10, lambda: (win.destroy(), self.set_language(code)))

        for code, label in LANGUAGES:
            selected = code == self.lang
            bg = ACCENT_LIGHT if selected else BG_CARD
            fg = ACCENT if selected else TEXT_PRIMARY
            row = tk.Frame(win, bg=bg, cursor="hand2")
            row.pack(fill="x", padx=18, pady=4)
            prefix = "✓  " if selected else "    "
            lbl = tk.Label(row, text=prefix + label, bg=bg, fg=fg,
                            font=(FONT_FAMILY, 11, "bold" if selected else "normal"),
                            anchor="w", padx=10, pady=12)
            lbl.pack(fill="x")
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, c=code: pick(c))

    def rebuild_ui(self):
        self.container.destroy()
        self.autostart_row = None
        self._build_layout()
        self.render_games()

    # -- layout ------------------------------------------------------------
    def _build_layout(self):
        self.container = container = tk.Frame(self.root, bg=BG_PAGE)
        container.pack(fill="both", expand=True)

        self.sidebar = sidebar = tk.Frame(container, bg=BG_SIDEBAR, width=285)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="∞  Infinite Launcher", bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
                 font=(FONT_FAMILY, 13, "bold"), anchor="w").pack(fill="x", padx=18, pady=(22, 18))

        self._nav_item(sidebar, self.t("nav_home"), selected=True)
        self._nav_item(sidebar, self.t("nav_scan"), command=self.scan_dialog)
        self._nav_item(sidebar, self.t("nav_add"), command=self.add_game)
        self._nav_item(sidebar, self.t("nav_remove"), command=self.remove_game)
        self._render_autostart_item()
        self._nav_item(sidebar, self.t("nav_languages"), command=self.language_dialog)

        main = tk.Frame(container, bg=BG_PAGE)
        main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(main, bg=BG_PAGE)
        header.pack(fill="x", padx=28, pady=(26, 4))
        tk.Label(header, text=self.t("header_title"), bg=BG_PAGE, fg=TEXT_PRIMARY,
                 font=(FONT_FAMILY, 22, "bold")).pack(anchor="w")
        tk.Label(header, text=self.t("header_subtitle"),
                 bg=BG_PAGE, fg=TEXT_SECONDARY, font=(FONT_FAMILY, 10)).pack(anchor="w", pady=(2, 0))

        scroll_area = tk.Frame(main, bg=BG_PAGE)
        scroll_area.pack(fill="both", expand=True, padx=20, pady=16)

        self.canvas = tk.Canvas(scroll_area, bg=BG_PAGE, highlightthickness=0)
        vsb = tk.Scrollbar(scroll_area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.list_holder = tk.Frame(self.canvas, bg=BG_PAGE)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_holder, anchor="nw")
        self.list_holder.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

        self.card = RoundedCard(self.list_holder, bg=BG_PAGE)
        self.card.pack(fill="x")

    def _nav_item(self, parent, text, selected=False, command=None):
        bg = ACCENT_LIGHT if selected else BG_SIDEBAR
        fg = ACCENT if selected else TEXT_PRIMARY
        row = tk.Frame(parent, bg=bg, cursor="hand2" if command else "")
        row.pack(fill="x", padx=10, pady=3)
        if selected:
            bar = tk.Frame(row, bg=ACCENT, width=3)
            bar.pack(side="left", fill="y")
        lbl = tk.Label(row, text=text, bg=bg, fg=fg, font=(FONT_FAMILY, 11),
                        anchor="w", padx=12, pady=9)
        lbl.pack(fill="x")
        if command:
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e: command())
                w.bind("<Enter>", lambda e: (row.config(bg="#f0f0f0"), lbl.config(bg="#f0f0f0")))
                w.bind("<Leave>", lambda e: (row.config(bg=bg), lbl.config(bg=bg)))
        return row

    def _render_autostart_item(self):
        if self.autostart_row is not None:
            self.autostart_row.destroy()
        self.autostart_row = self._nav_item(
            self.sidebar, self.t("nav_autostart"),
            selected=is_autostart_enabled(),
            command=self.toggle_autostart
        )

    def toggle_autostart(self):
        enable = not is_autostart_enabled()
        try:
            set_autostart(enable)
        except Exception as exc:
            messagebox.showerror(self.t("err_title"), self.t("autostart_err_msg", exc=exc))
            return
        # Deferred for the same reason as toggle_language: don't destroy the
        # widget that's still inside its own click callback.
        self.root.after(10, self._render_autostart_item)
        if enable:
            messagebox.showinfo(self.t("autostart_on_title"), self.t("autostart_on_msg"))
        else:
            messagebox.showinfo(self.t("autostart_off_title"), self.t("autostart_off_msg"))

    # -- game list -----------------------------------------------------
    def get_icon_photo(self, game, size=44):
        key = game.get("icon") or ("exe", game["target"])
        if key not in self.icon_cache:
            raw = None
            if game.get("icon") and os.path.isfile(game["icon"]):
                try:
                    raw = Image.open(game["icon"]).convert("RGBA")
                except Exception:
                    raw = None
            elif game["target"].lower().endswith(".exe"):
                raw = extract_exe_icon(game["target"], size=128)
            self.icon_cache[key] = raw
        raw = self.icon_cache[key]
        if raw is None:
            return None
        photo = ImageTk.PhotoImage(square_icon(raw).resize((size, size), Image.LANCZOS))
        self.icon_photos.append(photo)
        return photo

    def render_games(self):
        for widget in self.card.inner.winfo_children():
            widget.destroy()
        self.icon_photos.clear()

        if not self.games:
            tk.Label(self.card.inner, text=self.t("empty_state"),
                     bg=BG_CARD, fg=TEXT_SECONDARY, font=(FONT_FAMILY, 10),
                     padx=16, pady=20).pack(fill="x")
            return

        for idx, game in enumerate(self.games):
            row = tk.Frame(self.card.inner, bg=BG_CARD)
            row.pack(fill="x")

            content = tk.Frame(row, bg=BG_CARD)
            content.pack(fill="x", padx=16, pady=12)

            photo = self.get_icon_photo(game)
            if photo is not None:
                icon_widget = tk.Label(content, image=photo, bg=BG_CARD)
            else:
                icon_widget = avatar(content, game["name"])
            icon_widget.pack(side="left")

            text_col = tk.Frame(content, bg=BG_CARD)
            text_col.pack(side="left", fill="x", expand=True, padx=(12, 8))
            tk.Label(text_col, text=game["name"], bg=BG_CARD, fg=TEXT_PRIMARY,
                     font=(FONT_FAMILY, 11, "bold"), anchor="w", justify="left",
                     wraplength=200).pack(fill="x")
            target = game["target"]
            short = target if len(target) <= 40 else target[:37] + "..."
            tk.Label(text_col, text=short, bg=BG_CARD, fg=TEXT_SECONDARY,
                     font=(FONT_FAMILY, 9), anchor="w", justify="left",
                     wraplength=200).pack(fill="x")

            btn = RoundedButton(content, self.t("btn_start"), lambda g=game: self.launch_game(g),
                                 width=110, height=32, radius=16, bg=BG_CARD)
            btn.pack(side="right")

            edit_btn = RoundedButton(content, "", lambda g=game: self.change_icon_dialog(g),
                                      width=32, height=32, radius=16, bg=BG_CARD,
                                      fill="#f3f3f3", hover="#e5e5e5", fg=TEXT_SECONDARY,
                                      icon="pencil")
            edit_btn.pack(side="right", padx=(0, 8))

            if idx < len(self.games) - 1:
                tk.Frame(self.card.inner, bg=BORDER, height=1).pack(fill="x", padx=16)

    def launch_game(self, game):
        target = game["target"]
        try:
            if "://" in target or target.lower().startswith("shell:"):
                os.startfile(target)
            elif os.path.isfile(target):
                subprocess.Popen([target], cwd=os.path.dirname(target) or None)
            else:
                os.startfile(target)
        except Exception as exc:
            messagebox.showerror(
                self.t("err_start_title"),
                self.t("err_start_msg", name=game["name"], exc=exc, target=target)
            )

    # -- add / remove ----------------------------------------------------
    def add_game(self):
        name = simpledialog.askstring(self.t("add_title"), self.t("add_name_prompt"), parent=self.root)
        if not name:
            return

        choice = messagebox.askyesno(self.t("add_choice_title"), self.t("add_choice_msg"))
        if choice:
            path = filedialog.askopenfilename(
                title=self.t("filedialog_exe_title"),
                filetypes=[(self.t("filetype_programs"), "*.exe"), (self.t("filetype_all"), "*.*")]
            )
            if not path:
                return
            target = path
        else:
            target = simpledialog.askstring(self.t("add_link_title"), self.t("add_link_prompt"), parent=self.root)
            if not target:
                return

        self.games.append({"name": name, "target": target})
        save_games(self.games)
        self.render_games()

    def remove_game(self):
        if not self.games:
            messagebox.showinfo(self.t("info_title"), self.t("remove_none_msg"))
            return

        win = self._new_dialog(self.t("remove_title"), "320x430")

        listbox = tk.Listbox(win, font=(FONT_FAMILY, 11), bg=BG_CARD,
                              relief="flat", highlightthickness=1, highlightbackground=BORDER)
        for g in self.games:
            listbox.insert("end", g["name"])
        listbox.pack(fill="both", expand=True, padx=12, pady=12)
        listbox.selection_set(0)

        def do_remove():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning(
                    self.t("remove_none_selected_title"),
                    self.t("remove_none_selected_msg")
                )
                return
            removed = self.games.pop(sel[0])
            save_games(self.games)
            self.render_games()
            win.destroy()
            messagebox.showinfo(self.t("remove_done_title"), self.t("remove_done_msg", name=removed["name"]))

        RoundedButton(win, self.t("remove_btn"), do_remove, width=140, height=36,
                      fill="#c42b1c", hover="#a4271a", bg=BG_PAGE).pack(pady=(0, 14))

    # -- icon ----------------------------------------------------------
    def change_icon_dialog(self, game):
        choice = messagebox.askyesnocancel(
            self.t("icon_change_title"),
            self.t("icon_change_msg", name=game["name"])
        )
        if choice is None:
            return

        if choice:
            path = filedialog.askopenfilename(
                title=self.t("filedialog_image_title"),
                filetypes=[(self.t("filetype_images"), "*.png *.jpg *.jpeg *.bmp *.ico *.gif"),
                           (self.t("filetype_all"), "*.*")]
            )
            if not path:
                return
            try:
                img = Image.open(path)
                if getattr(img, "is_animated", False):
                    img.seek(0)
                img = img.convert("RGBA")
            except Exception as exc:
                messagebox.showerror(self.t("err_title"), self.t("err_image_load_msg", exc=exc))
                return
        else:
            exe_path = filedialog.askopenfilename(
                title=self.t("filedialog_icon_exe_title"),
                filetypes=[(self.t("filetype_programs"), "*.exe"), (self.t("filetype_all"), "*.*")]
            )
            if not exe_path:
                return
            img = extract_exe_icon(exe_path, size=128)
            if img is None:
                messagebox.showerror(self.t("err_title"), self.t("err_no_icon_msg"))
                return

        game["icon"] = store_custom_icon(img)
        save_games(self.games)
        self.render_games()

    # -- scan --------------------------------------------------------------
    def scan_dialog(self):
        win = self._new_dialog(self.t("scan_title"), "420x580")

        tk.Label(win, text=self.t("scan_header"), bg=BG_PAGE, fg=TEXT_PRIMARY,
                 font=(FONT_FAMILY, 13, "bold")).pack(anchor="w", padx=16, pady=(16, 2))
        status = tk.Label(win, text=self.t("scan_searching"), bg=BG_PAGE, fg=TEXT_SECONDARY,
                           font=(FONT_FAMILY, 10))
        status.pack(anchor="w", padx=16)

        list_frame = tk.Frame(win, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        list_frame.pack(fill="both", expand=True, padx=16, pady=12)

        canvas = tk.Canvas(list_frame, bg=BG_CARD, highlightthickness=0)
        vsb = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        inner = tk.Frame(canvas, bg=BG_CARD)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        vars_and_games = []
        existing_names = {g["name"].lower() for g in self.games}

        def populate():
            found = scan_installed_games()
            status.config(text=self.t("scan_found", n=len(found)) if found else self.t("scan_none"))
            for g in found:
                var = tk.BooleanVar(value=g["name"].lower() not in existing_names)
                row = tk.Checkbutton(inner, text=g["name"], variable=var, bg=BG_CARD,
                                      fg=TEXT_PRIMARY, font=(FONT_FAMILY, 10),
                                      anchor="w", selectcolor=BG_CARD, activebackground=BG_CARD)
                row.pack(fill="x", padx=8, pady=2)
                vars_and_games.append((var, g))

        win.after(50, populate)

        def add_selected():
            added = 0
            for var, g in vars_and_games:
                if var.get() and g["name"].lower() not in {x["name"].lower() for x in self.games}:
                    self.games.append(g)
                    added += 1
            if added:
                save_games(self.games)
                self.render_games()
            win.destroy()
            messagebox.showinfo(self.t("scan_done_title"), self.t("scan_done_msg", n=added))

        RoundedButton(win, self.t("scan_add_btn"), add_selected, width=220, height=38,
                      bg=BG_PAGE).pack(pady=(0, 16))


if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
