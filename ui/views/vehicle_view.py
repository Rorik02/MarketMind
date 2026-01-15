import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QScrollArea, QPushButton, QMessageBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class VehicleView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent_ctrl = parent
        self.theme = theme
        self.save_data = save_data or {}
        self.image_cache = {}
        self.all_vehicles = self.load_vehicles_data()
        self.setup_ui()

    def load_vehicles_data(self):
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "vehicles.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return []

    def get_cached_pixmap(self, img_name):
        if img_name in self.image_cache: return self.image_cache[img_name]
        img_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "vehicles", img_name)
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.image_cache[img_name] = pix
            return pix
        return None

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        header = QHBoxLayout()
        title = QLabel("🏎️ VEHICLE SHOWROOM")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.back_btn = QPushButton("⬅️ Back to Home")
        self.back_btn.setFixedSize(150, 35)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.back_btn)
        self.main_layout.addLayout(header)

        tabs_layout = QHBoxLayout()
        self.btn_my_garage = QPushButton("My Garage")
        self.btn_showroom = QPushButton("Dealership")
        for btn in [self.btn_my_garage, self.btn_showroom]:
            btn.setFixedHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            tabs_layout.addWidget(btn)
        
        self.btn_my_garage.clicked.connect(lambda: self.refresh_list("owned"))
        self.btn_showroom.clicked.connect(lambda: self.refresh_list("market"))
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

    def refresh_list(self, mode="owned"):
        self.container.setUpdatesEnabled(False)
        active = "background-color: #3a96dd; color: white; border-radius: 8px; font-weight: bold;"
        inactive = "background-color: #2a2a2a; color: white; border-radius: 8px;"
        self.btn_my_garage.setStyleSheet(active if mode == "owned" else inactive)
        self.btn_showroom.setStyleSheet(active if mode == "market" else inactive)

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        owned_ids = self.save_data.get('owned_vehicles', [])
        for veh in self.all_vehicles:
            is_owned = veh['id'] in owned_ids
            if (mode == "owned" and is_owned) or (mode == "market" and not is_owned):
                self.add_vehicle_card(veh, is_owned)
        self.container.setUpdatesEnabled(True)

    def add_vehicle_card(self, veh, is_owned):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet("background-color: #252525; border: 1px solid #444; border-radius: 12px;")
        c_lay = QHBoxLayout(card)
        c_lay.setContentsMargins(15, 10, 15, 10)

        img_lbl = QLabel()
        img_lbl.setFixedSize(160, 100)
        pix = self.get_cached_pixmap(veh['image'])
        if pix: 
            img_lbl.setPixmap(pix)
            img_lbl.setStyleSheet("border-radius: 6px; border: 1px solid #333;")
        else:
            img_lbl.setStyleSheet("background: #111; border-radius: 6px;")
            img_lbl.setText("NO IMAGE")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QVBoxLayout()
        info.addWidget(QLabel(f"<b>{veh['name']}</b>"))
        info.addWidget(QLabel(f"<font color='#2ecc71'>Price: ${veh['price']:,}</font>"))

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prestige = QLabel(f"⭐ {veh['prestige']} Prestige")
        prestige.setStyleSheet("background: #1a1a1a; padding: 5px; border-radius: 5px;")
        right.addWidget(prestige)
        
        if not is_owned:
            btn = QPushButton("BUY")
            btn.setFixedSize(100, 35)
            btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px; font-weight: bold;")
            btn.clicked.connect(lambda ch, v=veh: self.buy_vehicle(v))
            right.addWidget(btn)
        else:
            lbl = QLabel("OWNED")
            lbl.setStyleSheet("color: #2ecc71; font-weight: bold;")
            right.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        c_lay.addWidget(img_lbl)
        c_lay.addLayout(info)
        c_lay.addStretch()
        c_lay.addLayout(right)
        self.list_layout.addWidget(card)

    def buy_vehicle(self, veh):
        """Logika zakupu pojazdu z kompaktowym powiadomieniem."""
        if self.save_data.get('balance', 0) >= veh['price']:
            self.save_data['balance'] -= veh['price']
            if 'owned_vehicles' not in self.save_data: self.save_data['owned_vehicles'] = []
            self.save_data['owned_vehicles'].append(veh['id'])
            self.save_data['prestige'] = self.save_data.get('prestige', 0) + veh['prestige']
            
            if hasattr(self.parent_ctrl, 'update_money_display'): 
                self.parent_ctrl.update_money_display()

            # --- KOMPAKTOWE OKNO POWIADOMIENIA ---
            msg = QMessageBox(self)
            msg.setWindowTitle("Showroom")
            # Dodajemy emoji do tekstu, brak ikony usuwa pusty obszar po lewej
            msg.setText(f"🎉 <b>Congratulations!</b><br>You've purchased <b>{veh['name']}</b>!")
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #1a1a1a; border: none; }
                QLabel { color: white; font-size: 14px; padding: 10px 20px; min-width: 220px; }
                QPushButton { 
                    background-color: #27ae60; color: white; font-weight: bold; 
                    border-radius: 4px; min-width: 70px; height: 28px;
                    margin-right: 10px; margin-bottom: 5px; border: none;
                }
                QPushButton:hover { background-color: #2ecc71; }
            """)
            msg.exec()

            self.refresh_list("market")
        else:
            QMessageBox.warning(self, "Bank", "Insufficient funds!")

    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border: 1px solid {colors['tile_border']}; border-radius: 18px;")