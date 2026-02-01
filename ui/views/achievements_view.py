from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QFrame, QLabel
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import json, os

class AchievementsView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.theme = theme
        self.save_data = save_data or {}
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.title = QLabel("🏆 GLOBAL ACHIEVEMENTS")
        self.title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #f1c40f; margin-bottom: 10px;")
        self.layout.addWidget(self.title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(15)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def refresh_view(self, new_save_data):
        self.save_data = new_save_data
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)

        unlocked = self.save_data.get('unlocked_achievements', [])
        
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "achievements.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)['achievements']
                
            for i, ach in enumerate(data):
                is_unlocked = ach['id'] in unlocked
                card = self.create_achievement_card(ach, is_unlocked)
                self.grid.addWidget(card, i // 3, i % 3)
        except Exception as e:
            print(f"Error loading achievements UI: {e}")

    def create_achievement_card(self, ach, is_unlocked):
        card = QFrame()
        card.setFixedSize(285, 150) 
        
        bg = "#1e272e" if not is_unlocked else "#218c74"
        border = "#3d3d3d" if not is_unlocked else "#f1c40f"
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 12px;
                padding: 5px;
            }}
        """)
        
        lay = QVBoxLayout(card)
        lay.setSpacing(5)
        
        name = QLabel(f"{'🔒 ' if not is_unlocked else '⭐ '}{ach['name']}")
        name.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name.setStyleSheet("color: white; border: none;")
        name.setWordWrap(True)
        
        desc = QLabel(ach['description'])
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        desc.setStyleSheet("""
            color: #aaaaaa; 
            font-size: 11px; 
            border: none;
            background: transparent;
        """)
        
        lay.addWidget(name)
        lay.addWidget(desc, 1)
        
        status_text = "UNLOCKED" if is_unlocked else "LOCKED"
        status = QLabel(status_text)
        status.setStyleSheet(f"color: {'#f1c40f' if is_unlocked else '#555555'}; font-size: 9px; font-weight: bold; border: none;")
        lay.addWidget(status, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        return card