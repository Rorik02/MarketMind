import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QGridLayout, QPushButton
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class HomeView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.theme = theme
        self.save_data = save_data or {}
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # --- 1. TOP SECTION: PROFILE & SKILL POINTS ---
        top_container = QHBoxLayout()
        
        self.profile_box = QFrame()
        self.profile_box.setFixedWidth(500)
        profile_lay = QHBoxLayout(self.profile_box)
        profile_lay.setContentsMargins(15, 15, 15, 15)
        profile_lay.setSpacing(25)

        self.avatar_img = QLabel()
        self.avatar_img.setFixedSize(110, 110)
        avatar_file = self.save_data.get('avatar')
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "avatars", str(avatar_file))
        
        if os.path.exists(avatar_path):
            pix = QPixmap(avatar_path).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.avatar_img.setPixmap(pix)
        
        self.info_txt = QLabel()
        self.update_profile_text()
        
        profile_lay.addWidget(self.avatar_img)
        profile_lay.addWidget(self.info_txt)
        profile_lay.addStretch()

        self.skill_btn = QPushButton()
        self.update_skill_button()
        self.skill_btn.setFixedSize(220, 75)
        self.skill_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        top_container.addWidget(self.profile_box)
        top_container.addStretch()
        top_container.addWidget(self.skill_btn)
        self.main_layout.addLayout(top_container)

        # --- 2. GRID AREA ---
        grid = QGridLayout()
        grid.setSpacing(20)

        # 1. Household (Large - Span 2 rows)
        self.house_tile = self.create_module_tile("🏠 HOUSEHOLD", True)
        grid.addWidget(self.house_tile, 0, 0, 2, 1)

        # 2. Vehicles (Small)
        # Nadajemy nazwę obiektu, aby GameView mógł znaleźć przycisk przez findChild
        self.veh_tile = self.create_module_tile("🚗 VEHICLES", False, "Owned: 0\nGarage: Empty")
        self.veh_tile.setObjectName("VehiclesTile") 
        grid.addWidget(self.veh_tile, 0, 1)

        # 3. Valuables
        grid.addWidget(self.create_module_tile("💎 VALUABLES", False, "Watches, Art, Jewelry"), 0, 2)

        # 4. Employment
        grid.addWidget(self.create_module_tile("💼 EMPLOYMENT", False, "Status: Unemployed\nJob Market: 5 Offers"), 1, 1)

        # 5. Achievements
        grid.addWidget(self.create_module_tile("🏆 ACHIEVEMENTS", False, "Completed: 0 / 50\nGlobal Rank: N/A"), 1, 2)

        self.main_layout.addLayout(grid)
        self.main_layout.addStretch()

    def create_module_tile(self, title, is_large=False, default_status=""):
        tile = QFrame()
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(20, 20, 20, 20)

        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(t_lbl)

        if is_large:
            self.house_img_lbl = QLabel()
            self.house_img_lbl.setFixedSize(260, 160)
            self.house_img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.house_status_lbl = QLabel()
            self.house_status_lbl.setStyleSheet("color: #bbbbbb; font-size: 11px;")
            
            self.update_home_property_data()
            
            layout.addWidget(self.house_img_lbl)
            layout.addWidget(self.house_status_lbl)
        else:
            s_lbl = QLabel(default_status)
            s_lbl.setStyleSheet("color: #bbbbbb; font-size: 11px;")
            layout.addWidget(s_lbl)
            
        layout.addStretch()
        
        btn_lay = QHBoxLayout()
        # Przycisk "Manage"
        m_btn = QPushButton("Manage" if "ACHIEVEMENTS" not in title else "View All")
        m_btn.setFixedSize(100, 32)
        m_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_lay.addWidget(m_btn)
        btn_lay.addStretch()
        
        if is_large:
            own_lbl = QLabel("Owned")
            own_lbl.setStyleSheet("color: #2ecc71; font-weight: bold;")
            btn_lay.addWidget(own_lbl)

        layout.addLayout(btn_lay)
        return tile

    def refresh_view(self, new_save_data):
        self.save_data = new_save_data
        self.update_profile_text()
        self.update_skill_button()
        self.update_home_property_data()
        self.update_vehicle_status() # Dodana metoda odświeżania aut

    def update_profile_text(self):
        self.info_txt.setText(
            f"<font size='6' color='white'><b>{self.save_data.get('player_name')} {self.save_data.get('player_surname')}</b></font><br>"
            f"<font size='4' color='#aaaaaa'>Age: {self.save_data.get('age', 25)}<br>"
            f"Joined: {self.save_data.get('created', '').split(' ')[0]}</font>"
        )

    def update_skill_button(self):
        self.skill_btn.setText(f"⭐ Skill Points: {self.save_data.get('skill_points', 0)}\n(Click to upgrade)")

    def update_home_property_data(self):
        primary_id = self.save_data.get('primary_home', 'prop_00')
        owned_ids = self.save_data.get('owned_properties', [])
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "properties.json")
        
        img_name = "default.png"
        location = "N/A"
        prop_name = "N/A"
        total_upkeep = 0 

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                props = json.load(f)
                for p in props:
                    if p['id'] in owned_ids:
                        if p['id'] == primary_id:
                            img_name = p['image']
                            location = p['location']
                            prop_name = p['name']
                            total_upkeep += p['upkeep']
                        else:
                            total_upkeep += int(p['upkeep'] * 0.5)

        owned_count = len(owned_ids)
        status_text = (
            f"Current: {prop_name}<br>"
            f"Location: {location}<br>"
            f"Owned: {owned_count}<br>"
            f"Total Upkeep: <span style='color:#e74c3c; font-weight:bold;'>${total_upkeep:,}/month</span>"
        )

        self.house_status_lbl.setText(status_text)
        self.house_status_lbl.setTextFormat(Qt.TextFormat.RichText)

        img_path = os.path.join(base_path, "..", "..", "assets", "properties", img_name)
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(260, 160, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.house_img_lbl.setPixmap(pix)

    def update_vehicle_status(self):
        """Aktualizuje licznik i łączną wartość garażu z poprawioną grafiką."""
        owned_ids = self.save_data.get('owned_vehicles', [])
        count = len(owned_ids)
        total_value = 0
        
        # Wczytujemy ceny z JSON
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "vehicles.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                vehicles_data = json.load(f)
                for veh in vehicles_data:
                    if veh['id'] in owned_ids:
                        total_value += veh['price']

        if hasattr(self, 'veh_tile'):
            labels = self.veh_tile.findChildren(QLabel)
            if len(labels) >= 2:
                status_lbl = labels[1]
                # NOWY DESIGN: Wyraźna wartość kolekcji
                status_text = (
                    f"<span style='font-size:12px; color:#aaaaaa;'>Vehicles: {count}</span><br>"
                    f"<span style='font-size:11px; color:#aaaaaa;'>Collection Value:</span><br>"
                    f"<span style='font-size:15px; color:#2ecc71; font-weight:bold;'>${total_value:,}</span>"
                )
                status_lbl.setText(status_text)
                # KLUCZOWE: To naprawia błąd widocznych tagów <font> lub <span>
                status_lbl.setTextFormat(Qt.TextFormat.RichText)
                
    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border: 1px solid {colors['tile_border']}; border-radius: 18px;")
        self.profile_box.setStyleSheet("border: none; background: transparent;")
        self.avatar_img.setStyleSheet("border: 2px solid #3a96dd; border-radius: 12px; background: #1a1a1a;")

        tile_style = """
            QFrame { background-color: #222; border: 1px solid #333; border-radius: 15px; }
            QLabel { border: none; background: transparent; color: white; }
            QPushButton { background-color: #3a96dd; color: white; border-radius: 8px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #4fb2ff; }
        """
        self.skill_btn.setStyleSheet("QPushButton { background-color: #f1c40f; color: black; border-radius: 12px; font-weight: bold; border: 2px solid #d4ac0d; } QPushButton:hover { background-color: #f4d03f; }")

        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item.layout():
                for j in range(item.layout().count()):
                    w = item.layout().itemAt(j).widget()
                    if isinstance(w, QFrame) and w != self.profile_box:
                        w.setStyleSheet(tile_style)