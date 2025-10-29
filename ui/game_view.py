from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class GameView(QWidget):
    """Placeholder for the main game screen (market, portfolio, etc.)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = None

        # Basic layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Temporary label for testing
        self.label = QLabel("Game Screen")
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_mode(self, mode: str):
        """Sets the current game mode and updates the UI accordingly."""
        self.mode = mode
        self.label.setText(f"Game Mode: {mode.upper()}")

        # Change background color for visual distinction
        if mode == "simulation":
            self.setStyleSheet("background-color: #f5f5ff;")  # light blue
        else:
            self.setStyleSheet("background-color: #fffaf0;")  # light beige
