import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QScrollArea, QPushButton, QMessageBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class HouseholdView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent_ctrl = parent
        self.theme = theme
        self.save_data = save_data or {}
        
        self.image_cache = {} 
        
        self.all_properties = self.load_properties_data()
        
        self.setup_ui()

    def load_properties_data(self):
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "properties.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Błąd ładowania nieruchomości: {e}")
            return []

    def get_cached_pixmap(self, img_name):
        """Ładuje i skaluje obraz tylko raz, potem pobiera z pamięci."""
        if img_name in self.image_cache:
            return self.image_cache[img_name]

        img_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "properties", img_name)
        
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(140, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.image_cache[img_name] = pix
            return pix
        return None

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header = QHBoxLayout()
        title = QLabel("🏘️ REAL ESTATE MANAGEMENT")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.back_btn = QPushButton("⬅️ Back to Home")
        self.back_btn.setFixedSize(150, 35)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.back_btn)
        self.main_layout.addLayout(header)

        # Tabs
        tabs_layout = QHBoxLayout()
        self.btn_my_assets = QPushButton("My Properties")
        self.btn_market = QPushButton("Real Estate Market")
        for btn in [self.btn_my_assets, self.btn_market]:
            btn.setFixedHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            tabs_layout.addWidget(btn)
        
        self.btn_my_assets.clicked.connect(lambda: self.refresh_list(mode="owned"))
        self.btn_market.clicked.connect(lambda: self.refresh_list(mode="market"))
        self.main_layout.addLayout(tabs_layout)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(15)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.refresh_list(mode="owned")

    def refresh_list(self, mode="owned"):
        self.container.setUpdatesEnabled(False)
        
        if mode == "owned":
            self.btn_my_assets.setStyleSheet("background-color: #3a96dd; color: white; border-radius: 8px; font-weight: bold;")
            self.btn_market.setStyleSheet("background-color: #2a2a2a; color: white; border-radius: 8px;")
        else:
            self.btn_market.setStyleSheet("background-color: #3a96dd; color: white; border-radius: 8px; font-weight: bold;")
            self.btn_my_assets.setStyleSheet("background-color: #2a2a2a; color: white; border-radius: 8px;")

        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        owned_ids = self.save_data.get('owned_properties', ["prop_00"])
        for prop in self.all_properties:
            is_owned = prop['id'] in owned_ids
            if (mode == "owned" and is_owned) or (mode == "market" and not is_owned):
                self.add_property_card(prop, is_owned)
        
        self.container.setUpdatesEnabled(True)

    def add_property_card(self, prop, is_owned):
        card = QFrame()
        card.setFixedHeight(125)
        card.setObjectName("PropertyCard")
        c_lay = QHBoxLayout(card)
        c_lay.setContentsMargins(15, 10, 15, 10)

        img_lbl = QLabel()
        img_lbl.setFixedSize(140, 90)
        pix = self.get_cached_pixmap(prop['image'])
        
        if pix:
            img_lbl.setPixmap(pix)
            img_lbl.setStyleSheet("border-radius: 5px; border: 1px solid #333;")
        else:
            img_lbl.setStyleSheet("background: #111; border-radius: 5px; color: #444;")
            img_lbl.setText("NO IMAGE")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_vbox = QVBoxLayout()
        name_lbl = QLabel(f"<b>{prop['name']}</b>")
        name_lbl.setFont(QFont("Arial", 14))
        loc_lbl = QLabel(f"<font color='#aaaaaa'>{prop['location']}</font>")
        price_lbl = QLabel(f"<font color='#2ecc71'>Value: ${prop['price']:,}</font>")
        
        is_primary = self.save_data.get('primary_home') == prop['id']
        if is_owned and not is_primary:
            tax = int(prop['upkeep'] * 0.5)
            upkeep_text = f"<font color='#f39c12'>Idle Tax: ${tax:,} (50%)</font>"
        else:
            upkeep_text = f"<font color='#e74c3c'>Full Upkeep: ${prop['upkeep']:,}</font>"
            
        upkeep_lbl = QLabel(upkeep_text)
        upkeep_lbl.setFont(QFont("Arial", 10))

        info_vbox.addWidget(name_lbl)
        info_vbox.addWidget(loc_lbl)
        info_vbox.addWidget(price_lbl)
        info_vbox.addWidget(upkeep_lbl)

        right_vbox = QVBoxLayout()
        right_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prestige_lbl = QLabel(f"⭐ {prop['prestige']} Prestige")
        prestige_lbl.setStyleSheet("background: #1a1a1a; padding: 5px; border-radius: 5px; border: 1px solid #333;")
        
        action_btn = QPushButton()
        action_btn.setFixedSize(140, 40)
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if is_owned:
            if is_primary:
                action_btn.setText("CURRENT HOME")
                action_btn.setEnabled(False)
                action_btn.setStyleSheet("background-color: #27ae60; color: white; border: 2px solid #2ecc71; border-radius: 8px; font-weight: bold;")
            else:
                action_btn.setText("SET AS PRIMARY")
                action_btn.setStyleSheet("background-color: #34495e; color: white; border-radius: 8px; font-weight: bold;")
                action_btn.clicked.connect(lambda ch, pid=prop['id']: self.set_primary(pid))
        else:
            action_btn.setText("BUY PROPERTY")
            action_btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px; font-weight: bold;")
            action_btn.clicked.connect(lambda ch, p=prop: self.buy_property(p))

        right_vbox.addWidget(prestige_lbl)
        right_vbox.addWidget(action_btn)
        c_lay.addWidget(img_lbl)
        c_lay.addLayout(info_vbox)
        c_lay.addStretch()
        c_lay.addLayout(right_vbox)
        self.list_layout.addWidget(card)

    def buy_property(self, prop):
        current_balance = self.save_data.get('balance', 0)
        if current_balance >= prop['price']:
            price = prop['price']
            
            self.save_data['balance'] -= price
            
            if 'owned_properties' not in self.save_data: 
                self.save_data['owned_properties'] = []
            self.save_data['owned_properties'].append(prop['id'])
            
            if hasattr(self.parent_ctrl, 'log_transaction'):
                self.parent_ctrl.log_transaction(
                    "Nieruchomość", 
                    f"Zakup: {prop['name']}", 
                    -price
                )

            if hasattr(self.parent_ctrl, 'update_money_display'): 
                self.parent_ctrl.update_money_display()
                
            QMessageBox.information(self, "Success", f"Congratulations! You bought {prop['name']}!")
            self.refresh_list(mode="owned")
        else:
            QMessageBox.warning(self, "Insufficient Funds", "You don't have enough money!")

    def set_primary(self, prop_id):
        self.save_data['primary_home'] = prop_id
        if hasattr(self.parent_ctrl, 'view_home'): self.parent_ctrl.view_home.refresh_view(self.save_data)
        self.refresh_list(mode="owned")

    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border: 1px solid {colors['tile_border']}; border-radius: 18px;")
        self.container.setStyleSheet("QFrame#PropertyCard { background-color: #252525; border: 1px solid #444; border-radius: 12px; } QLabel { border: none; color: white; }")