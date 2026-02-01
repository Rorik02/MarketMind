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

        top_container = QHBoxLayout()
        
        self.profile_box = QFrame()
        self.profile_box.setFixedWidth(500)
        profile_lay = QHBoxLayout(self.profile_box)
        profile_lay.setContentsMargins(15, 15, 15, 15)
        profile_lay.setSpacing(25)

        self.avatar_img = QLabel()
        self.avatar_img.setFixedSize(110, 110)
        avatar_file = self.save_data.get('avatar', 'default.png')
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "avatars", str(avatar_file))
        
        if os.path.exists(avatar_path):
            pix = QPixmap(avatar_path).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.avatar_img.setPixmap(pix)
        
        self.info_txt = QLabel()
        profile_lay.addWidget(self.avatar_img)
        profile_lay.addWidget(self.info_txt)
        profile_lay.addStretch()

        top_container.addWidget(self.profile_box)
        top_container.addStretch()
        self.main_layout.addLayout(top_container)

        grid = QGridLayout()
        grid.setSpacing(20)

    
        self.house_tile = self.create_module_tile("🏠 HOUSEHOLD", True, target_view_index=6)
        self.house_tile.setObjectName("HouseTile")
        grid.addWidget(self.house_tile, 0, 0, 2, 1)

        self.veh_tile = self.create_module_tile("🚗 VEHICLES", False, target_view_index=7)
        self.veh_tile.setObjectName("VehiclesTile") 
        grid.addWidget(self.veh_tile, 0, 1)

        self.valuables_tile = self.create_module_tile("💎 VALUABLES", False, target_view_index=8)
        self.valuables_tile.setObjectName("ValuablesTile")
        grid.addWidget(self.valuables_tile, 0, 2)

        self.employment_tile = self.create_module_tile("💼 EMPLOYMENT", False, target_view_index=9)
        self.employment_tile.setObjectName("EmploymentTile")
        grid.addWidget(self.employment_tile, 1, 1)

        self.achievements_tile = self.create_module_tile("🏆 ACHIEVEMENTS", False, "Completed: 0 / 50", target_view_index=12)
        self.achievements_tile.setObjectName("AchievementsTile")
        grid.addWidget(self.achievements_tile, 1, 2)

        self.main_layout.addLayout(grid)
        self.main_layout.addStretch()
        
        self.refresh_view(self.save_data)

    def create_module_tile(self, title, is_large=False, default_status="", target_view_index=None):
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
            layout.addWidget(self.house_img_lbl)
            layout.addWidget(self.house_status_lbl)
        else:
            s_lbl = QLabel(default_status)
            s_lbl.setStyleSheet("color: #bbbbbb; font-size: 11px;")
            layout.addWidget(s_lbl)
            
        layout.addStretch()
        btn_lay = QHBoxLayout()
        
        m_btn = QPushButton("Manage" if "ACHIEVEMENTS" not in title else "View All")
        m_btn.setFixedSize(100, 32)
        m_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if target_view_index is not None:
            m_btn.clicked.connect(lambda: self.parent().parent().switch_view(target_view_index))

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
        self.update_home_property_data()
        self.update_vehicle_status()
        self.update_valuables_status()
        self.update_employment_status()
        self.update_profile_text()
        unlocked_list = self.save_data.get('unlocked_achievements', [])
        current_prestige = self.save_data.get('prestige', 0)
        max_prestige = self.save_data.get('max_prestige', 123458350)

        if hasattr(self, 'achievements_tile'):
            labels = self.achievements_tile.findChildren(QLabel)
            if len(labels) >= 2:
                labels[1].setText(
                    f"Completed: {len(unlocked_list)} / 49\n"
                )

    def update_profile_text(self):
        p_house = self.calculate_house_prestige_with_bonus()
        p_veh = self.calculate_category_prestige("vehicles.json", "owned_vehicles")
        p_val = self.calculate_category_prestige("valuables.json", "owned_valuables")
        total_prestige = p_house + p_veh + p_val
        self.save_data['prestige'] = total_prestige
        
        from datetime import datetime
        dob_str = self.save_data.get('date_of_birth', '2002-03-21')
        current_date_str = self.save_data.get('current_game_date', '2031-12-12') 
        
        try:
            dob = datetime.strptime(dob_str[:10], "%Y-%m-%d")
            curr = datetime.strptime(current_date_str[:10], "%Y-%m-%d")
            calculated_age = curr.year - dob.year
            if (curr.month, curr.day) < (dob.month, dob.day):
                calculated_age -= 1
        except:
            calculated_age = self.save_data.get('age', 23)

        self.info_txt.setText(
            f"<font size='6' color='white'><b>{self.save_data.get('player_name')} {self.save_data.get('player_surname')}</b></font><br>"
            f"<font size='4' color='#aaaaaa'>Age: {calculated_age}<br>"
            f"Born: {dob_str}<br>" 
            f"<font color='#f1c40f'>🏆 Global Prestige: {total_prestige:,}</font></font>"
        )

    def update_employment_status(self):
        job_id = self.save_data.get('current_job')
        job_title = "Unemployed"
        salary_text = "$0"
        
        if job_id:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "jobs.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                    for j in jobs:
                        if j['id'] == job_id:
                            job_title = j['title']
                            salary = j['base_salary']
                            months = self.save_data.get('job_months', 0)
                            for m in j.get('milestones', []):
                                if months >= m['months']: salary += m['bonus']
                            salary_text = f"${salary:,}"
                            break

        active_course = self.save_data.get('active_course')
        course_status = "None"
        if active_course:
            days_left = max(0, active_course['remaining_hours'] // 24)
            course_status = f"<font color='#3a96dd'>{active_course['name']} ({days_left}d left)</font>"

        if hasattr(self, 'employment_tile'):
            labels = self.employment_tile.findChildren(QLabel)
            if len(labels) >= 2:
                status_lbl = labels[1]
                status_lbl.setWordWrap(True)
                status_lbl.setTextFormat(Qt.TextFormat.RichText)
                status_lbl.setText(
                    f"<div style='line-height: 120%;'>"
                    f"Job: <font color='white'>{job_title}</font><br>"
                    f"Salary: <font color='#2ecc71'>{salary_text}/mo</font><br>"
                    f"Course: {course_status}</div>"
                )

    def calculate_house_prestige_with_bonus(self):
        primary_id = self.save_data.get('primary_home', 'prop_00')
        owned_ids = self.save_data.get('owned_properties', [])
        total = 0
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "properties.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                props = json.load(f)
                for p in props:
                    if p['id'] in owned_ids:
                        total += (p.get('prestige', 0) * (2 if p['id'] == primary_id else 1))
        return total

    def calculate_category_prestige(self, json_file, save_key):
        owned_ids = self.save_data.get(save_key, [])
        total = 0
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", json_file)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for i in items:
                    if i['id'] in owned_ids:
                        total += i.get('prestige', 0)
        return total

    def update_home_property_data(self):
        primary_id = self.save_data.get('primary_home', 'prop_00')
        owned_ids = self.save_data.get('owned_properties', [])
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "..", "..", "data", "properties.json")
        img_name, location, prop_name, total_upkeep, display_prestige = "default.png", "N/A", "N/A", 0, 0
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                props = json.load(f)
                for p in props:
                    if p['id'] in owned_ids:
                        if p['id'] == primary_id:
                            display_prestige += (p.get('prestige', 0) * 2)
                            total_upkeep += p['upkeep']
                            img_name, location, prop_name = p['image'], p['location'], p['name']
                        else:
                            display_prestige += p.get('prestige', 0)
                            total_upkeep += int(p['upkeep'] * 0.5)
        
        if hasattr(self, 'house_status_lbl'):
            self.house_status_lbl.setText(
                f"Current: {prop_name}<br>Location: {location}<br>"
                f"Upkeep: <span style='color:#e74c3c; font-weight:bold;'>${total_upkeep:,}/mo</span><br>"
                f"<span style='color:#f1c40f;'>⭐ House Prestige: {display_prestige:,}</span>"
            )
        img_path = os.path.join(base_path, "..", "..", "assets", "properties", img_name)
        if os.path.exists(img_path) and hasattr(self, 'house_img_lbl'):
            pix = QPixmap(img_path).scaled(260, 160, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.house_img_lbl.setPixmap(pix)

    def update_vehicle_status(self):
        owned_ids = self.save_data.get('owned_vehicles', [])
        total_value = self.calculate_category_value("vehicles.json", "owned_vehicles")
        total_prestige = self.calculate_category_prestige("vehicles.json", "owned_vehicles")
        if hasattr(self, 'veh_tile'):
            labels = self.veh_tile.findChildren(QLabel)
            if len(labels) >= 2:
                labels[1].setText(f"Vehicles: {len(owned_ids)}<br>Value: <span style='color:#2ecc71;'>${total_value:,}</span><br>"
                                f"<span style='color:#f1c40f;'>⭐ Garage Prestige: {total_prestige:,}</span>")

    def update_valuables_status(self):
        owned_ids = self.save_data.get('owned_valuables', [])
        total_value = self.calculate_category_value("valuables.json", "owned_valuables")
        total_prestige = self.calculate_category_prestige("valuables.json", "owned_valuables")
        if hasattr(self, 'valuables_tile'):
            labels = self.valuables_tile.findChildren(QLabel)
            if len(labels) >= 2:
                labels[1].setText(f"Items: {len(owned_ids)}<br>Value: <span style='color:#f1c40f;'>${total_value:,}</span><br>"
                                f"<span style='color:#f1c40f;'>⭐ Collection Prestige: {total_prestige:,}</span>")

    def calculate_category_value(self, json_file, save_key):
        owned_ids = self.save_data.get(save_key, [])
        total = 0
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", json_file)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for i in items:
                    if i['id'] in owned_ids:
                        total += i.get('price', 0)
        return total

    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border: 1px solid {colors['tile_border']}; border-radius: 18px;")
        self.profile_box.setStyleSheet("border: none; background: transparent;")
        self.avatar_img.setStyleSheet("border: 2px solid #3a96dd; border-radius: 12px; background: #1a1a1a;")
        tile_style = "QFrame { background-color: #222; border: 1px solid #333; border-radius: 15px; } QLabel { border: none; background: transparent; color: white; } QPushButton { background-color: #3a96dd; color: white; border-radius: 8px; font-weight: bold; border: none; } QPushButton:hover { background-color: #4fb2ff; }"
        for t in [self.house_tile, self.veh_tile, self.valuables_tile, self.employment_tile, self.achievements_tile]:
            t.setStyleSheet(tile_style)

    