from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt

class GameView(QWidget):
    """Main game screen placeholder with a temporary back button for testing."""

    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.save_data = save_data or {}

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

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

        # Temporary button to return to Main Menu
        self.btn_back = QPushButton("🔙 Back to Main Menu")
        self.btn_back.setFixedSize(250, 50)
        self.btn_back.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_back.clicked.connect(self.return_to_menu)
        layout.addWidget(self.btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_theme()

    def return_to_menu(self):
        """Trigger the transition back to Main Menu in MainWindow."""
        if self.parent and hasattr(self.parent, 'show_main_menu'):
            self.parent.show_main_menu()

    def apply_theme(self):
        """Apply the current theme colors to the view and button."""
        if not self.theme:
            return
        c = self.theme.get_colors()
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        
        self.label.setStyleSheet(f"color: {c['text']};")
        
        # Style the back button to match the theme
        self.btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['button_bg']};
                color: white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {c['button_hover']};
            }}
        """)