import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


class ThemeManager:
    """Handles loading, saving, and applying the color theme (dark/light)."""

    def __init__(self):
        self.dark_mode = False
        self.load_theme()

    def load_theme(self):
        """Load theme setting from config.json."""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    self.dark_mode = data.get("dark_mode", False)
        except Exception:
            self.dark_mode = False

    def save_theme(self):
        """Save the current theme setting to config.json."""
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"dark_mode": self.dark_mode}, f, indent=4)
        except Exception as e:
            print("Error saving theme:", e)

    def toggle_theme(self, value: bool):
        """Set theme on/off and save it."""
        self.dark_mode = value
        self.save_theme()

    def get_colors(self):
        """Return a dict of colors depending on mode."""
        if self.dark_mode:
            return {
                "background": "#1e1e1e",
                "text": "#ffffff",
                "button_bg": "#0A84FF",
                "button_hover": "#339CFF",
                "button_pressed": "#0063B1",
                "tile_bg": "#2a2a2a",
                "tile_border": "#4a4a4a",
                "highlight": "#0078D7",
            }
        else:
            return {
                "background": "#ffffff",
                "text": "#000000",
                "button_bg": "#0078D7",
                "button_hover": "#0063B1",
                "button_pressed": "#004E8C",
                "tile_bg": "#f2f2f2",
                "tile_border": "#cccccc",
                "highlight": "#0078D7",
            }
    def load_theme(self):
        """Load theme and last save info."""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    self.dark_mode = data.get("dark_mode", False)
                    self.last_save = data.get("last_save", None)
            else:
                self.last_save = None
        except Exception:
            self.dark_mode = False
            self.last_save = None

    def save_theme(self):
        """Save theme and last save info."""
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(
                    {"dark_mode": self.dark_mode, "last_save": getattr(self, "last_save", None)},
                    f, indent=4
                )
        except Exception as e:
            print("Error saving theme:", e)

    def set_last_save(self, filename: str):
        """Save last opened/created save name."""
        self.last_save = filename
        self.save_theme()
