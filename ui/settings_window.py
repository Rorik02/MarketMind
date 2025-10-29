from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class SettingsWindow(QDialog):
    """Settings dialog for toggling night mode."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title_label = QLabel("Display Settings")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.night_mode_checkbox = QCheckBox("Night Mode 🌙")
        self.night_mode_checkbox.setFont(QFont("Arial", 12))
        self.night_mode_checkbox.setChecked(self.theme.dark_mode)
        layout.addWidget(self.night_mode_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        apply_button = QPushButton("Apply")
        apply_button.setFixedSize(100, 40)
        apply_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #0063B1; }
            QPushButton:pressed { background-color: #004E8C; }
        """)
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def apply_settings(self):
        """Save and apply global theme setting."""
        self.theme.toggle_theme(self.night_mode_checkbox.isChecked())
        self.parent.apply_theme()
        self.close()
