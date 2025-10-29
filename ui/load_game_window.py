import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QScrollArea, QWidget, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
from core.theme_manager import ThemeManager


class LoadGameWindow(QDialog):
    """Window for loading and deleting saved games."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme or ThemeManager()
        self.setWindowTitle("Load Game")
        self.setFixedSize(500, 600)
        self.setModal(True)

        self.saves_dir = os.path.join(os.path.dirname(__file__), "..", "saves")
        os.makedirs(self.saves_dir, exist_ok=True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.title = QLabel("Load Game")
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # Scroll area for saves
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)

        self.setLayout(layout)

        self.load_saves()
        self.apply_theme()

    # === THEME HANDLING ===
    def apply_theme(self):
        """Apply theme colors."""
        c = self.theme.get_colors()
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.title.setStyleSheet(f"color: {c['text']}; margin-bottom: 10px;")

    # === LOAD SAVES ===
    def load_saves(self):
        """Display all available save files as cards with load & delete options."""
        # Clear layout first
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        save_files = [f for f in os.listdir(self.saves_dir) if f.endswith(".json")]
        if not save_files:
            no_save_label = QLabel("No saved games found.")
            no_save_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_save_label.setFont(QFont("Arial", 12))
            self.scroll_layout.addWidget(no_save_label)
            return

        for save_file in sorted(save_files, reverse=True):
            file_path = os.path.join(self.saves_dir, save_file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except Exception:
                continue

            # Card frame
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 10px;
                }
                QFrame:hover {
                    border: 2px solid #0078D7;
                }
            """)
            frame_layout = QVBoxLayout(frame)

            # Basic info
            info = QLabel(
                f"<b>{data['player_name']} {data['player_surname']}</b>  "
                f"|  Mode: {data['mode']}<br>"
                f"💰 Balance: ${data['balance']:,}  |  Age: {data['player_age']}<br>"
                f"🕒 Last Played: {data['created']}"
            )
            info.setStyleSheet("font-size: 12px;")
            info.setWordWrap(True)
            frame_layout.addWidget(info)

            # Buttons (Load / Delete)
            btn_layout = QHBoxLayout()
            btn_load = QPushButton("▶ Load")
            btn_delete = QPushButton("🗑 Delete")

            for b in [btn_load, btn_delete]:
                b.setFixedHeight(35)
                b.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                b.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_load.clicked.connect(lambda _, f=save_file: self.load_selected_save(f))
            btn_delete.clicked.connect(lambda _, f=save_file, w=frame: self.delete_save(f, w))

            btn_layout.addWidget(btn_load)
            btn_layout.addWidget(btn_delete)
            frame_layout.addLayout(btn_layout)

            self.scroll_layout.addWidget(frame)

    # === LOAD SELECTED SAVE ===
    def load_selected_save(self, filename):
        """Load selected save file."""
        path = os.path.join(self.saves_dir, filename)
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load save file:\n{e}")
            return

        # Save this as last loaded game
        self.theme.set_last_save(filename)

        QMessageBox.information(
            self, "Game Loaded",
            f"Loaded save:\n{data['player_name']} {data['player_surname']} ({data['mode']})"
        )
        self.close()

    # === DELETE SAVE ===
    def delete_save(self, filename, widget):
        """Delete a save file after user confirmation."""
        confirm = QMessageBox.question(
            self,
            "Delete Save",
            f"Are you sure you want to delete save:\n\n{filename}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                os.remove(os.path.join(self.saves_dir, filename))
                widget.setParent(None)
                QMessageBox.information(self, "Deleted", f"Save '{filename}' has been deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete save:\n{e}")
