import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui.main_menu import MainMenu
from ui.game_view import GameView 
from core.theme_manager import ThemeManager
from utils.market_provider import MarketProvider

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeQuest")
        self.setMinimumSize(1280, 720)
        self.theme = ThemeManager()

        print("Inicjalizacja giełdy... Proszę czekać.")
        self.market_provider = MarketProvider()
        self.global_market_snapshot = self.market_provider.get_market_data()
        print("Giełda gotowa.")

        self.menu = MainMenu(self)
        self.setCentralWidget(self.menu)

        self.showFullScreen()

    def start_game(self, save_data):
        if hasattr(self, 'menu') and self.menu:
            self.menu.deleteLater()
            self.menu = None
            
        if 'market_data' not in save_data:
            save_data['market_data'] = self.global_market_snapshot
            print("Dane rynkowe przekazane do nowego zapisu bez pobierania.")
            
        self.game_view = GameView(self, self.theme, save_data)
        self.setCentralWidget(self.game_view)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen(): self.showNormal()
            else: self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()

    def show_main_menu(self):
        if hasattr(self, 'game_view') and self.game_view:
            self.game_view.deleteLater()
            self.game_view = None
        from ui.main_menu import MainMenu
        self.menu = MainMenu(self)
        self.setCentralWidget(self.menu)