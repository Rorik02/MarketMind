import os
import json
from PyQt6.QtWidgets import (
    QApplication,  # ✅ DODANY IMPORT
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem,
    QSizePolicy, QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt6.QtCore import Qt
from ui.settings_window import SettingsWindow
from ui.new_game_window import NewGameWindow
from ui.load_game_window import LoadGameWindow
from core.theme_manager import ThemeManager


class MainMenu(QWidget):
    """Main menu with Start, Load, Continue, Settings, and Exit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = ThemeManager()
        self.last_save_data = None
        self.init_ui()

        self.apply_theme() #
        self.update_last_save_info() #

    def init_ui(self):
        """Build full layout."""
        # === MAIN HORIZONTAL LAYOUT ===
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(60, 60, 60, 60)
        main_layout.setSpacing(60)

        # === LEFT PANEL: LAST SAVE INFO ===
        self.last_save_info = QFrame()
        self.last_save_info.setFixedWidth(350)
        self.last_save_info.setLayout(QVBoxLayout())
        self.last_save_info.layout().setContentsMargins(20, 20, 20, 20)
        self.last_save_info.layout().setSpacing(8)

        self.last_save_title = QLabel("Last Save Info")
        self.last_save_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.last_save_player = QLabel()
        self.last_save_details = QLabel()
        self.last_save_time = QLabel()

        for lbl in [self.last_save_title, self.last_save_player, self.last_save_details, self.last_save_time]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.last_save_info.layout().addWidget(lbl)

        self.last_save_info.layout().addStretch()
        main_layout.addWidget(self.last_save_info, alignment=Qt.AlignmentFlag.AlignVCenter)

        # === CENTER PANEL: LOGO + TITLE ===
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(30)

        self.logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(220, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("$")
            self.logo_label.setFont(QFont("Arial", 96, QFont.Weight.Bold))
            self.logo_label.setStyleSheet("color: #2b9348;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.logo_label)

        self.title_label = QLabel("MarketMind")
        self.title_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("margin-bottom: 30px;")
        center_layout.addWidget(self.title_label)

        main_layout.addLayout(center_layout, stretch=1)

        # === RIGHT PANEL: MENU BUTTONS ===
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.setSpacing(20)

        self.btn_continue = QPushButton("▶ CONTINUE LAST SAVE")
        self.btn_start = QPushButton("🆕 START NEW GAME")
        self.btn_load = QPushButton("📂 LOAD GAME")
        self.btn_settings = QPushButton("⚙ SETTINGS")
        self.btn_exit = QPushButton("❌ EXIT GAME")

        for btn in [self.btn_continue, self.btn_start, self.btn_load, self.btn_settings, self.btn_exit]:
            btn.setFixedSize(280, 60)
            btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            right_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        # === SIGNALS ===
        self.btn_continue.clicked.connect(self.continue_last_save)
        self.btn_start.clicked.connect(self.open_new_game)
        self.btn_load.clicked.connect(self.open_load_game)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_exit.clicked.connect(self.exit_game)

        self.apply_theme()
        self.update_last_save_info()

    # === THEME ===
    def apply_theme(self):
        c = self.theme.get_colors()
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.title_label.setStyleSheet(f"color: {c['text']}; margin-bottom: 30px;")

        # Buttons
        for btn in [self.btn_continue, self.btn_start, self.btn_load, self.btn_settings]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['button_bg']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: {c['button_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {c['button_pressed']};
                }}
            """)

        # Exit button (red)
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #b52b27;
            }
        """)

        # Last save panel
        self.last_save_info.setStyleSheet(f"""
            QFrame {{
                background-color: {c['tile_bg']};
                border: 2px solid {c['tile_border']};
                border-radius: 10px;
            }}
        """)
        for lbl in [self.last_save_title, self.last_save_player, self.last_save_details, self.last_save_time]:
            lbl.setStyleSheet(f"color: {c['text']};")

    # === UPDATE LAST SAVE PANEL ===
    def update_last_save_info(self):
        last_save = getattr(self.theme, "last_save", None)
        saves_dir = os.path.join(os.path.dirname(__file__), "..", "saves")

        if not last_save:
            self.last_save_info.hide()
            self.btn_continue.setEnabled(False)
            return

        save_path = os.path.join(saves_dir, last_save)
        if not os.path.exists(save_path):
            self.last_save_info.hide()
            self.btn_continue.setEnabled(False)
            return

        try:
            with open(save_path, "r") as f:
                data = json.load(f)
                self.last_save_data = data
        except Exception:
            self.last_save_info.hide()
            return

        self.last_save_info.show()
        self.btn_continue.setEnabled(True)

        name = data.get('player_name', 'Unknown')
        surname = data.get('player_surname', '')
        balance = data.get('balance', 0)
        age = data.get('player_age', '??')
        mode = data.get('mode', 'Standard')
        created = data.get('created', 'N/A')

        self.last_save_player.setText(f"👤 {name} {surname}")
        self.last_save_details.setText(f"💰 Balance: ${balance:,}  |  Age: {age}  |  Mode: {mode}")
        self.last_save_time.setText(f"🕒 Last Played: {created}")

    # === BUTTON ACTIONS ===
    def continue_last_save(self):
        if not self.last_save_data:
            QMessageBox.warning(self, "No Save", "No previous save found.")
            return
        QMessageBox.information(
            self,
            "Continue Game",
            f"Loading last save:\n"
            f"{self.last_save_data['player_name']} {self.last_save_data['player_surname']} "
            f"({self.last_save_data['mode']})"
        )
        if self.parent and hasattr(self.parent, 'start_game'):
            self.parent.start_game(self.last_save_data)

    def open_new_game(self):
        win = NewGameWindow(self.parent, self.theme)
        win.exec()
        self.theme.load_theme()
        self.apply_theme()
        self.update_last_save_info()

    def open_load_game(self):
        win = LoadGameWindow(self.parent, self.theme)
        win.exec()
        self.theme.load_theme()
        self.apply_theme()
        self.update_last_save_info()

    def open_settings(self):
        win = SettingsWindow(self, self.theme)
        win.exec()
        self.theme.load_theme()
        self.apply_theme()

    def show_main_menu(self):
        """Switch from Game View back to the Main Menu."""
        if hasattr(self, 'game_view') and self.game_view:
            self.game_view.deleteLater()
            self.game_view = None
            
        # Import inside the method to avoid circular imports
        from ui.main_menu import MainMenu
        # Re-initialize the Main Menu and pass 'self' as parent
        self.menu = MainMenu(self) 
        self.setCentralWidget(self.menu) #

    def exit_game(self):
        """Close the entire application."""
        confirm = QMessageBox.question(
            self, "Exit Game", "Are you sure you want to quit MarketMind?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            app = QApplication.instance()
            if app is not None:
                app.quit()


