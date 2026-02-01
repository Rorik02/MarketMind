import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QScrollArea, QPushButton, QMessageBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class ValuablesView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent_ctrl = parent
        self.theme = theme
        self.save_data = save_data or {}
        self.image_cache = {}
        self.all_valuables = self.load_data()
        self.setup_ui()

    def load_data(self):
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "valuables.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []

    def get_cached_pixmap(self, img_name):
        if img_name in self.image_cache: return self.image_cache[img_name]
        img_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "valuables", img_name)
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.image_cache[img_name] = pix
            return pix
        return None

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        header = QHBoxLayout()
        title = QLabel("💎 LUXURY VALUABLES")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.back_btn = QPushButton("⬅️ Back to Home")
        self.back_btn.setFixedSize(150, 35)
        self.back_btn.clicked.connect(self.safe_go_back)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.back_btn)
        self.main_layout.addLayout(header)

        tabs_layout = QHBoxLayout()
        self.btn_my = QPushButton("My Collection")
        self.btn_market = QPushButton("Auction House")
        for b in [self.btn_my, self.btn_market]:
            b.setFixedHeight(45)
            tabs_layout.addWidget(b)
        
        self.btn_my.clicked.connect(lambda: self.refresh_list("owned"))
        self.btn_market.clicked.connect(lambda: self.refresh_list("market"))
        self.main_layout.addLayout(tabs_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.refresh_list("owned")

    def safe_go_back(self):
        if hasattr(self.parent_ctrl, 'workspace_stack'):
            self.parent_ctrl.workspace_stack.setCurrentIndex(0)
        elif hasattr(self.parent_ctrl, 'return_to_home'):
            self.parent_ctrl.return_to_home()


    def refresh_list(self, mode="owned"):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        owned_ids = self.save_data.get('owned_valuables', [])
        for item in self.all_valuables:
            is_owned = item['id'] in owned_ids
            if (mode == "owned" and is_owned) or (mode == "market" and not is_owned):
                self.add_card(item, is_owned)

    def add_card(self, item, is_owned):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet("background-color: #252525; border: 1px solid #444; border-radius: 12px;")
        lay = QHBoxLayout(card)

        img_lbl = QLabel()
        img_lbl.setFixedSize(160, 100)
        pix = self.get_cached_pixmap(item['image'])
        if pix: img_lbl.setPixmap(pix)

        info = QVBoxLayout()
        info.addWidget(QLabel(f"<b>{item['name']}</b>"))
        info.addWidget(QLabel(f"<font color='#aaaaaa'>{item['category']}</font>"))
        info.addWidget(QLabel(f"<font color='#2ecc71'>Value: ${item['price']:,}</font>"))
        info.addWidget(QLabel(f"<font color='#f1c40f'>⭐ Prestige: +{item['prestige']}</font>"))

        right = QVBoxLayout()
        if not is_owned:
            btn = QPushButton("BUY")
            btn.setFixedSize(100, 35)
            btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 8px;")
            btn.clicked.connect(lambda ch, i=item: self.buy_item(i))
            right.addWidget(btn)
        else:
            right.addWidget(QLabel("COLLECTED"))

        lay.addWidget(img_lbl)
        lay.addLayout(info)
        lay.addStretch()
        lay.addLayout(right)
        self.list_layout.addWidget(card)

    def buy_item(self, item):
        """Logika zakupu przedmiotu z zapisem do historii i powiadomieniem."""
        if self.save_data.get('balance', 0) >= item['price']:
            price = item['price']
            
            self.save_data['balance'] -= price
            if 'owned_valuables' not in self.save_data: 
                self.save_data['owned_valuables'] = []
            self.save_data['owned_valuables'].append(item['id'])
            self.save_data['prestige'] = self.save_data.get('prestige', 0) + item['prestige']
            
            if hasattr(self.parent_ctrl, 'log_transaction'):
                self.parent_ctrl.log_transaction(
                    "Drogocenności", 
                    f"Zakup: {item['name']}", 
                    -price
                )
            
            if hasattr(self.parent_ctrl, 'update_money_display'): 
                self.parent_ctrl.update_money_display()

            msg = QMessageBox(self)
            msg.setWindowTitle("Auction House")
            msg.setText(f"✨ <b>Item Acquired!</b><br>You are now the owner of:<br><b>{item['name']}</b>")
            
            msg.setStyleSheet("""
                QMessageBox { 
                    background-color: #1a1a1a; 
                    border: 2px solid #2ecc71; 
                    border-radius: 10px;
                }
                QLabel { 
                    color: white; 
                    font-size: 14px; 
                    padding: 10px; 
                    min-width: 300px;  /* Zwiększona minimalna szerokość */
                }
                QPushButton { 
                    background-color: #27ae60; 
                    color: white; 
                    font-weight: bold; 
                    border-radius: 6px; 
                    min-width: 100px; 
                    height: 35px; 
                    border: none;
                    margin-bottom: 10px;
                }
                QPushButton:hover { background-color: #2ecc71; }
            """)
            
            for label in msg.findChildren(QLabel):
                label.setWordWrap(True)
            
            msg.exec()
            
            self.refresh_list("market")
        else:
            QMessageBox.warning(self, "Bank", "Insufficient funds!")

    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border: 1px solid {colors['tile_border']}; border-radius: 18px;")