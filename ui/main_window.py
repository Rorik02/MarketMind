import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui.main_menu import MainMenu
from ui.game_view import GameView 
from core.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    """Main window that handles fullscreen mode and app layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeQuest")
        self.setMinimumSize(1280, 720)
        self.theme = ThemeManager()


        # Load main menu
        self.menu = MainMenu(self)
        self.setCentralWidget(self.menu)

        # Start fullscreen
        self.showFullScreen()

    def start_game(self, save_data):
        """
        Switch the central widget from MainMenu to GameView.
        :param save_data: Dictionary containing the loaded or new player data.
        """
        # Remove the main menu if it exists
        if hasattr(self, 'menu') and self.menu:
            self.menu.deleteLater()
            self.menu = None
            
        # Initialize and set the GameView as the central widget
        self.game_view = GameView(self, self.theme, save_data)
        self.setCentralWidget(self.game_view)
            
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for fullscreen toggle and exit."""
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()

    def show_main_menu(self):
            """Switch from Game View back to the Main Menu."""
        # Remove the game view widget if it exists
            if hasattr(self, 'game_view') and self.game_view:
                self.game_view.deleteLater()
                self.game_view = None
            # Re-initialize the Main Menu
            from ui.main_menu import MainMenu
            self.menu = MainMenu(self)
            self.setCentralWidget(self.menu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
