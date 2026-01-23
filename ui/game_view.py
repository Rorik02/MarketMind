import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QFrame, QPushButton, QStackedWidget, QMessageBox, QLineEdit)
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt

# Importujemy modularne widoki
from ui.views.home_view import HomeView
from ui.views.household_view import HouseholdView
from ui.views.vehicle_view import VehicleView 
from ui.views.valuables_view import ValuablesView
from ui.views.employment_view import EmploymentView

class GameView(QWidget):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.save_data = save_data or {}
        
        # Inicjalizacja czasu
        date_str = self.save_data.get('created', '2026-01-14 00:00')
        self.current_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # 1. HEADER
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # 2. CONTENT AREA
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(20)
        
        self.side_menu = self.create_side_menu()
        
        # Workspace Stack - Zarządzanie widokami
        self.workspace_stack = QStackedWidget()
        
        # Inicjalizacja widoków
        self.view_home = HomeView(self, self.theme, self.save_data)
        self.view_dashboard = self.create_placeholder_view("📊 Dashboard", "Financial statistics and charts.")
        self.view_markets = self.create_placeholder_view("📈 Markets", "Exchange and stock trading.")
        self.view_portfolio = self.create_placeholder_view("💼 Portfolio", "Your assets and investments.")
        self.view_business = self.create_placeholder_view("🏢 Business", "Companies and management.")
        self.view_system = self.create_system_menu_view()
        self.view_household = HouseholdView(self, self.theme, self.save_data)
        self.view_vehicles = VehicleView(self, self.theme, self.save_data)
        self.view_valuables = ValuablesView(self, self.theme, self.save_data)
        self.view_employment = EmploymentView(self, self.theme, self.save_data)
        
        # Dodanie do stosu
        self.workspace_stack.addWidget(self.view_home)      # 0
        self.workspace_stack.addWidget(self.view_dashboard) # 1
        self.workspace_stack.addWidget(self.view_markets)   # 2
        self.workspace_stack.addWidget(self.view_portfolio) # 3
        self.workspace_stack.addWidget(self.view_business)  # 4
        self.workspace_stack.addWidget(self.view_system)    # 5
        self.workspace_stack.addWidget(self.view_household) # 6
        self.workspace_stack.addWidget(self.view_vehicles)  # 7
        self.workspace_stack.addWidget(self.view_valuables) # 8
        self.workspace_stack.addWidget(self.view_employment)# 9

        # --- LOGIKA PRZEŁĄCZANIA WIDOKÓW (POŁĄCZENIA) ---
        self.view_household.back_btn.clicked.connect(self.open_home)
        self.view_vehicles.back_btn.clicked.connect(self.open_home)
        self.view_valuables.back_btn.clicked.connect(self.open_home)
        self.view_employment.back_btn.clicked.connect(self.open_home)

        self.view_home.house_tile.findChild(QPushButton).clicked.connect(self.open_household_manager)
        
        veh_tile = self.view_home.findChild(QFrame, "VehiclesTile")
        if veh_tile:
            veh_btn = veh_tile.findChild(QPushButton)
            if veh_btn: veh_btn.clicked.connect(self.open_vehicle_manager)
        
        val_tile = self.view_home.findChild(QFrame, "ValuablesTile")
        if val_tile:
            val_btn = val_tile.findChild(QPushButton)
            if val_btn: val_btn.clicked.connect(self.open_valuables_manager)

        emp_tile = self.view_home.findChild(QFrame, "EmploymentTile")
        if emp_tile:
            emp_btn = emp_tile.findChild(QPushButton)
            if emp_btn: emp_btn.clicked.connect(self.open_employment_manager)

        self.content_layout.addWidget(self.side_menu, 1)
        self.content_layout.addWidget(self.workspace_stack, 4)
        self.main_layout.addLayout(self.content_layout)
        
        self.connect_menu_logic()
        self.apply_theme()

    # --- METODY NAWIGACJI ---
    def open_home(self):
        self.view_home.refresh_view(self.save_data)
        self.workspace_stack.setCurrentIndex(0)
        self.btn_system.setText("⚙️ SYSTEM")

    def open_employment_manager(self):
        self.view_employment.refresh_tabs()
        self.workspace_stack.setCurrentIndex(9)

    def open_household_manager(self): self.workspace_stack.setCurrentIndex(6)
    def open_vehicle_manager(self): self.workspace_stack.setCurrentIndex(7)
    def open_valuables_manager(self): self.workspace_stack.setCurrentIndex(8)

    # --- LOGIKA CZASU I FINANSÓW ---
    def advance_time(self, hours):
        self.current_datetime += timedelta(hours=hours)
        self.update_date_display()
        self.save_data['created'] = self.current_datetime.strftime("%Y-%m-%d %H:%M")
        
        if self.save_data.get('active_course'):
            course = self.save_data['active_course']
            course['remaining_hours'] -= hours
            
            if course['remaining_hours'] <= 0:
                if 'completed_courses' not in self.save_data: 
                    self.save_data['completed_courses'] = []
                if course['id'] not in self.save_data['completed_courses']:
                    self.save_data['completed_courses'].append(course['id'])
                
                self.save_data['active_course'] = None
                QMessageBox.information(self, "Education", f"Course Finished: {course['name']}")

        # ODŚWIEŻANIE UI NA ŻYWO
        current_idx = self.workspace_stack.currentIndex()
        if current_idx == 0:
            self.workspace_stack.currentWidget().refresh_view(self.save_data)
        elif current_idx == 9:
            self.workspace_stack.currentWidget().refresh_tabs()

        if hours >= 720: # +1m
            self.process_monthly_finances()

    def process_monthly_finances(self):
        job_id = self.save_data.get('current_job')
        salary = 0
        if job_id:
            self.save_data['job_months'] = self.save_data.get('job_months', 0) + 1
            salary = self.calculate_salary_with_milestones(job_id, self.save_data['job_months'])
        
        expenses = self.calculate_total_property_upkeep()
        net = salary - expenses
        self.save_data['balance'] += net
        self.update_money_display()
        self.view_home.refresh_view(self.save_data)
        
        QMessageBox.information(self, "Raport Finansowy", f"Wypłata: ${salary:,}\nKoszty życia: ${expenses:,}\nBilans: ${net:,}")

    def calculate_salary_with_milestones(self, job_id, months):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
                for j in jobs:
                    if j['id'] == job_id:
                        total = j['base_salary']
                        for m in j.get('milestones', []):
                            if months >= m['months']: total += m['bonus']
                        return total
        except: return 0
        return 0

    def calculate_total_property_upkeep(self):
        owned_ids = self.save_data.get('owned_properties', [])
        primary_id = self.save_data.get('primary_home', 'prop_00')
        total = 0
        path = os.path.join(os.path.dirname(__file__), "..", "data", "properties.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                props = json.load(f)
                for p in props:
                    if p['id'] in owned_ids:
                        total += p['upkeep'] if p['id'] == primary_id else int(p['upkeep'] * 0.5)
        except: pass
        return total

    # --- UI COMPONENTS ---
    def create_header(self):
        frame = QFrame()
        frame.setFixedHeight(100)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        self.player_area = QWidget()
        self.player_area.setStyleSheet("background: transparent; border: none;")
        p_layout = QHBoxLayout(self.player_area)
        p_layout.setContentsMargins(0, 0, 0, 0)
        
        self.avatar_lbl = QLabel()
        avatar_file = self.save_data.get('avatar', 'default.png')
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "assets", "avatars", str(avatar_file))
        if os.path.exists(avatar_path):
            pix = QPixmap(avatar_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.avatar_lbl.setPixmap(pix)
            
        self.player_info = QLabel(f"<b>{self.save_data.get('player_name', 'Player')}</b><br><font color='#aaaaaa'>Executive Manager</font>")
        p_layout.addWidget(self.avatar_lbl)
        p_layout.addWidget(self.player_info)

        self.money_lbl = QLabel(f"${self.save_data.get('balance', 0):,.2f}")
        self.money_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.money_lbl.setStyleSheet("color: #2ecc71; border: none; background: transparent;")
        self.money_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.right_container = QWidget()
        self.right_container.setStyleSheet("background: transparent; border: none;")
        r_layout = QHBoxLayout(self.right_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(10)

        self.date_lbl = QLabel()
        self.date_lbl.setStyleSheet("border: none; background: transparent;")
        self.update_date_display()
        r_layout.addWidget(self.date_lbl)
        
        self.time_btns = []
        for label, hours in [("+1h", 1), ("+1d", 24), ("+1w", 168), ("+1m", 720)]:
            btn = QPushButton(label)
            btn.setFixedSize(60, 38) 
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0px;
                }
                QPushButton:hover { background-color: #4a4a4a; }
            """)
            btn.clicked.connect(lambda ch, h=hours: self.advance_time(h))
            r_layout.addWidget(btn)
            self.time_btns.append(btn)

        self.btn_system = QPushButton("⚙️ SYSTEM")
        self.btn_system.setFixedSize(110, 40)
        self.btn_system.setStyleSheet("border: none; background-color: #3a96dd; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_system.clicked.connect(self.toggle_system_menu)
        r_layout.addWidget(self.btn_system)

        layout.addWidget(self.player_area, 0)
        layout.addStretch(1)
        layout.addWidget(self.money_lbl, 2)
        layout.addStretch(1)
        layout.addWidget(self.right_container, 0)
        return frame

    def create_placeholder_view(self, title_text, desc_text):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel(title_text); t.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        d = QLabel(desc_text); layout.addWidget(t, alignment=Qt.AlignmentFlag.AlignCenter); layout.addWidget(d, alignment=Qt.AlignmentFlag.AlignCenter)
        return frame

    def create_system_menu_view(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("SYSTEM SETTINGS")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        self.sys_btns = []
        actions = [
            ("💾 Save Game", self.save_game_logic), 
            ("💾 Save & Exit", self.save_and_exit_logic), 
            ("🚪 Exit Without Saving", self.return_to_menu), 
            ("⬅️ Back to Game", self.toggle_system_menu)
        ]

        for text, func in actions:
            btn = QPushButton(text)
            btn.setFixedSize(320, 65)
            btn.clicked.connect(func)
            layout.addWidget(btn)
            self.sys_btns.append(btn)

        # --- KONSOLA DEWELOPERSKA ---
        console_container = QFrame()
        console_container.setFixedWidth(320)
        console_container.setStyleSheet("background: #000; border: 1px solid #0f0; border-radius: 5px; margin-top: 20px;")
        console_lay = QVBoxLayout(console_container)
        
        console_title = QLabel("> DEVELOPER CONSOLE")
        console_title.setStyleSheet("color: #0f0; font-family: 'Courier New'; font-size: 10px; border: none;")
        
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Type command (e.g. money 100000)...")
        self.console_input.setStyleSheet("color: #0f0; background: transparent; border: none; font-family: 'Courier New';")
        self.console_input.returnPressed.connect(self.process_console)
        
        console_lay.addWidget(console_title)
        console_lay.addWidget(self.console_input)
        layout.addWidget(console_container)
        
        return frame

    def process_console(self):
        text = self.console_input.text().lower().split()
        if not text: return
        result = self.execute_console_command(text)
        self.console_input.clear()
        self.console_input.setPlaceholderText(f"Result: {result}")

    def execute_console_command(self, parts):
        command = parts[0]
        args = parts[1:]

        if command == "money" and len(args) > 0:
            try:
                amount = float(args[0])
                self.save_data['balance'] += amount
                self.update_money_display()
                self.view_home.refresh_view(self.save_data)
                return f"Added ${amount:,.2f}"
            except: return "Error"

        elif command == "prestige" and len(args) > 0:
            try:
                amount = int(args[0])
                self.save_data['prestige_bonus'] = self.save_data.get('prestige_bonus', 0) + amount
                self.view_home.refresh_view(self.save_data)
                return f"Added {amount} prestige bonus"
            except: return "Error"

        return "Unknown command"

    def save_and_exit_logic(self):
        self.save_game_logic()
        self.return_to_menu()

    def save_game_logic(self):
        surname = self.save_data.get('player_surname', 'default')
        path = os.path.join(os.path.dirname(__file__), "..", "saves", f"{surname}.json")
        with open(path, 'w', encoding='utf-8') as f: json.dump(self.save_data, f, indent=4)
        QMessageBox.information(self, "System", "Zapisano!")

    def return_to_menu(self):
        if self.parent: self.parent.show_main_menu()

    def create_side_menu(self):
        frame = QFrame()
        frame.setFixedWidth(230)
        layout = QVBoxLayout(frame)
        layout.setSpacing(18)
        layout.setContentsMargins(12, 25, 12, 25)
        self.menu_btns = []
        items = ["🏠 HOME", "📊 Dashboard", "📈 Markets", "💼 Portfolio", "🏢 Business"]
        for text in items:
            btn = QPushButton(text)
            btn.setFixedHeight(65)
            layout.addWidget(btn)
            self.menu_btns.append(btn)
        layout.addStretch()
        return frame

    def update_date_display(self):
        self.date_lbl.setText(f"📅 {self.current_datetime.strftime('%Y-%m-%d')}\n⏰ {self.current_datetime.strftime('%H:%M')}")

    def update_money_display(self):
        self.money_lbl.setText(f"${self.save_data.get('balance', 0):,.2f}")

    def toggle_system_menu(self):
        if self.workspace_stack.currentIndex() != 5: self.workspace_stack.setCurrentIndex(5)
        else: self.workspace_stack.setCurrentIndex(0)

    def connect_menu_logic(self):
        for i, btn in enumerate(self.menu_btns):
            btn.clicked.connect(lambda checked, index=i: self.workspace_stack.setCurrentIndex(index))

    def apply_theme(self):
        if not self.theme: return
        c = self.theme.get_colors()
        s = f"QFrame {{ background-color: {c['tile_bg']}; border: 1px solid {c['tile_border']}; border-radius: 18px; }}"
        self.header.setStyleSheet(s); self.side_menu.setStyleSheet(s)
        self.view_home.apply_theme(c); self.view_household.apply_theme(c); self.view_vehicles.apply_theme(c); self.view_valuables.apply_theme(c); self.view_employment.apply_theme(c)
        tile_style = f"QPushButton {{ background-color: #2a2a2a; color: {c['text']}; border: 1px solid #444; border-radius: 12px; text-align: left; padding-left: 20px; font-weight: bold; font-size: 15px; }}"
        for btn in self.menu_btns: btn.setStyleSheet(tile_style)
        self.btn_system.setStyleSheet("background: #3a96dd; color: white; border-radius: 5px; font-weight: bold;")
        for b in self.time_btns: b.setStyleSheet("background: #3a3a3a; color: white; border-radius: 5px; font-weight: bold;")