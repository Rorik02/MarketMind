from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt

class GameView(QWidget):
    """Placeholder for the main game screen (market, portfolio, etc.)."""

    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.save_data = save_data or {}

        # Main layout for game interface
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Welcome message using loaded player data
        player_name = self.save_data.get('player_name', 'Player')
        difficulty = self.save_data.get('difficulty', 'Unknown')
        
        welcome_text = (
            f"Welcome, {player_name}!\n"
            f"Difficulty: {difficulty}\n\n"
            "Something will be here someday..."
        )
        
        self.label = QLabel(welcome_text)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Initial theme application
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme colors from the theme manager."""
        if not self.theme:
            return
        c = self.theme.get_colors()
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.label.setStyleSheet(f"color: {c['text']};")