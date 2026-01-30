import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui.main_menu import MainMenu
from ui.game_view import GameView 
from core.theme_manager import ThemeManager
from utils.market_provider import MarketProvider

class MainWindow(QMainWindow):
    """Główne okno obsługujące logikę startową i widoki."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeQuest")
        self.setMinimumSize(1280, 720)
        self.theme = ThemeManager()

        # --- NOWOŚĆ: Inicjalizacja danych rynkowych przy starcie ---
        print("Inicjalizacja giełdy... Proszę czekać.")
        self.market_provider = MarketProvider()
        # Pobieramy dane raz - jeśli jest plik, potrwa to ułamek sekundy
        self.global_market_snapshot = self.market_provider.get_market_data()
        print("Giełda gotowa.")

        # Load main menu
        self.menu = MainMenu(self)
        self.setCentralWidget(self.menu)

        # Start fullscreen
        self.showFullScreen()

    def start_game(self, save_data):
        """Uruchamia grę, wstrzykując przygotowane wcześniej dane rynkowe."""
        if hasattr(self, 'menu') and self.menu:
            self.menu.deleteLater()
            self.menu = None
            
        # WSTRZYKNIĘCIE DANYCH: Jeśli to nowa gra, dodajemy snapshot do save_data
        if 'market_data' not in save_data:
            save_data['market_data'] = self.global_market_snapshot # Użyj załadowanego RAMu
            print("Dane rynkowe przekazane do nowego zapisu bez pobierania.")
            
        # Initialize and set the GameView as the central widget
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