import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui.main_menu import MainMenu


class MainWindow(QMainWindow):
    """Main window that handles fullscreen mode and app layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeQuest")
        self.setMinimumSize(1280, 720)

        # Load main menu
        self.menu = MainMenu(self)
        self.setCentralWidget(self.menu)

        # Start fullscreen
        self.showFullScreen()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for fullscreen toggle and exit."""
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
