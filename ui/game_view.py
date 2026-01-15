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
from ui.views.vehicle_view import VehicleView # DODANO IMPORT

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
        self.view_vehicles = VehicleView(self, self.theme, self.save_data) # DODANO WIDOK POJAZDÓW
        
        # Dodanie do stosu (ważna kolejność indeksów!)
        self.workspace_stack.addWidget(self.view_home)      # 0
        self.workspace_stack.addWidget(self.view_dashboard) # 1
        self.workspace_stack.addWidget(self.view_markets)   # 2
        self.workspace_stack.addWidget(self.view_portfolio) # 3
        self.workspace_stack.addWidget(self.view_business)  # 4
        self.workspace_stack.addWidget(self.view_system)    # 5
        self.workspace_stack.addWidget(self.view_household) # 6
        self.workspace_stack.addWidget(self.view_vehicles)  # 7 - DODANO INDEKS 7
        
        # --- LOGIKA PRZEŁĄCZANIA WIDOKÓW (POŁĄCZENIA) ---
        
        # Nawigacja dla Household (Domy)
        self.view_home.house_tile.findChild(QPushButton).clicked.connect(self.open_household_manager)
        self.view_household.back_btn.clicked.connect(self.open_home)

        # Nawigacja dla Vehicles (Pojazdy) - Szukanie przycisku w kafelku o nazwie VehiclesTile
        veh_btn = self.view_home.findChild(QFrame, "VehiclesTile").findChild(QPushButton)
        veh_btn.clicked.connect(self.open_vehicle_manager)
        self.view_vehicles.back_btn.clicked.connect(self.open_home)

        self.content_layout.addWidget(self.side_menu, 1)
        self.content_layout.addWidget(self.workspace_stack, 4)
        self.main_layout.addLayout(self.content_layout)
        
        self.connect_menu_logic()
        self.apply_theme()

    # --- METODY NAWIGACJI ---
    def open_household_manager(self):
        self.workspace_stack.setCurrentIndex(6)
        self.btn_system.setText("⚙️ SYSTEM")

    def open_vehicle_manager(self):
        """Przełącza na widok pojazdów (Index 7)."""
        self.workspace_stack.setCurrentIndex(7)
        self.btn_system.setText("⚙️ SYSTEM")

    def open_home(self):
        self.view_home.refresh_view(self.save_data) # Odświeżamy widok przy powrocie
        self.workspace_stack.setCurrentIndex(0)

    def create_header(self):
        frame = QFrame()
        frame.setFixedHeight(100)
        # Główny layout nagłówka
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # --- 1. LEWA STRONA: PROFIL (Brak obramowania) ---
        self.player_area = QWidget()
        self.player_area.setStyleSheet("background: transparent; border: none;") # USUWA RAMKI
        p_layout = QHBoxLayout(self.player_area)
        p_layout.setContentsMargins(0, 0, 0, 0)
        
        self.avatar_lbl = QLabel()
        avatar_file = self.save_data.get('avatar')
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "assets", "avatars", str(avatar_file))
        if os.path.exists(avatar_path):
            pix = QPixmap(avatar_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.avatar_lbl.setPixmap(pix)
            
        self.player_info = QLabel(f"<b>{self.save_data.get('player_name', 'Player')}</b><br><font color='#aaaaaa'>Executive Manager</font>")
        p_layout.addWidget(self.avatar_lbl)
        p_layout.addWidget(self.player_info)

        # --- 2. ŚRODEK: PIENIĄDZE ---
        self.money_lbl = QLabel(f"${self.save_data.get('balance', 0):,.2f}")
        self.money_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.money_lbl.setStyleSheet("color: #2ecc71; border: none; background: transparent;")
        self.money_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- 3. PRAWA STRONA: CZAS I SYSTEM (Przesunięte w lewo, bez ramek) ---
        self.right_container = QWidget()
        self.right_container.setStyleSheet("background: transparent; border: none;") # USUWA RAMKI
        r_layout = QHBoxLayout(self.right_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(10)

        # Data i Godzina (Zmniejszona szerokość, by zrobić miejsce)
        self.date_lbl = QLabel()
        self.date_lbl.setStyleSheet("border: none; background: transparent;")
        self.update_date_display()
        r_layout.addWidget(self.date_lbl)
        
        # PRZYCISKI CZASU
        self.time_btns = []
        for label, hours in [("+1h", 1), ("+1d", 24), ("+1w", 168), ("+1m", 720)]:
            btn = QPushButton(label)
            # ZWIĘKSZAMY szerokość do 60px i ustawiamy konkretny styl
            btn.setFixedSize(60, 38) 
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # STYLIZACJA: border:none (jak chciałeś) + usunięcie paddingu, by litery weszły
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0px; /* To kluczowe, żeby litery nie były ucinane */
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            
            btn.clicked.connect(lambda ch, h=hours: self.advance_time(h))
            r_layout.addWidget(btn)
            self.time_btns.append(btn)

        # PRZYCISK SYSTEM - również bez ramki i z marginesem po prawej
        self.btn_system = QPushButton("⚙️ SYSTEM")
        self.btn_system.setFixedSize(110, 40)
        self.btn_system.setStyleSheet("border: none; background-color: #3a96dd; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_system.clicked.connect(self.toggle_system_menu)
        r_layout.addWidget(self.btn_system)

        # MONTAŻ NAGŁÓWKA
        layout.addWidget(self.player_area, 0) # Lewo: Profil
        layout.addStretch(1)                  # Elastyczna spacja (popycha resztę w prawo, ale zachowuje środek)
        layout.addWidget(self.money_lbl, 2)   # Środek: Kasa (większa waga, by była centralnie)
        layout.addStretch(1)                  # Elastyczna spacja
        layout.addWidget(self.right_container, 0) # Prawo: Czas i System
        
        return frame
    

    def create_placeholder_view(self, title_text, desc_text):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel(title_text)
        t.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        d = QLabel(desc_text)
        layout.addWidget(t, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(d, alignment=Qt.AlignmentFlag.AlignCenter)
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
        for text, func in [("💾 Save Game", self.save_game_logic), 
                           ("💾 Save & Exit", self.save_and_exit_logic), 
                           ("🚪 Exit Without Saving", self.return_to_menu), 
                           ("⬅️ Back to Game", self.toggle_system_menu)]:
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
        self.console_input.setPlaceholderText("Type command...")
        self.console_input.setStyleSheet("color: #0f0; background: transparent; border: none; font-family: 'Courier New';")
        self.console_input.returnPressed.connect(self.process_console)
        
        console_lay.addWidget(console_title)
        console_lay.addWidget(self.console_input)
        layout.addWidget(console_container)
        
        return frame

    def process_console(self):
        text = self.console_input.text()
        result = self.execute_console_command(text)
        self.console_input.clear()
        self.console_input.setPlaceholderText(f"Result: {result}")

    def execute_console_command(self, text):
        parts = text.lower().split()
        if not parts: return ""
        command = parts[0]
        args = parts[1:]

        if command == "money" and len(args) > 0:
            try:
                amount = float(args[0])
                self.save_data['balance'] += amount
                self.update_money_display()
                self.view_home.refresh_view(self.save_data)
                return f"Added ${amount:,.2f}"
            except ValueError: return "Error: Invalid number."

        elif command == "prestige" and len(args) > 0:
            try:
                amount = int(args[0])
                self.save_data['prestige'] = max(0, self.save_data.get('prestige', 0) + amount)
                self.view_home.refresh_view(self.save_data)
                return f"Prestige set to {self.save_data['prestige']}"
            except ValueError: return "Error: Invalid integer."

        return "Unknown command."

    def connect_menu_logic(self):
        for i, btn in enumerate(self.menu_btns):
            btn.clicked.connect(lambda checked, index=i: self.switch_view(index))

    def switch_view(self, index):
        self.workspace_stack.setCurrentIndex(index)
        self.btn_system.setText("⚙️ SYSTEM")

    def toggle_system_menu(self):
        if self.workspace_stack.currentIndex() != 5:
            self.workspace_stack.setCurrentIndex(5)
            self.btn_system.setText("⬅️ BACK")
        else:
            self.workspace_stack.setCurrentIndex(0)
            self.btn_system.setText("⚙️ SYSTEM")

    def advance_time(self, hours):
        self.current_datetime += timedelta(hours=hours)
        self.update_date_display()
        self.save_data['created'] = self.current_datetime.strftime("%Y-%m-%d %H:%M")
        if hours >= 720: # +1m
            self.process_monthly_expenses()

    def process_monthly_expenses(self):
        owned_ids = self.save_data.get('owned_properties', [])
        primary_id = self.save_data.get('primary_home', 'prop_00')
        total_upkeep = 0
        
        # Pobieramy koszty TYLKO z nieruchomości (Household)
        for prop in self.view_household.all_properties:
            if prop['id'] in owned_ids:
                if prop['id'] == primary_id:
                    total_upkeep += prop['upkeep']
                else:
                    total_upkeep += int(prop['upkeep'] * 0.5)

        if total_upkeep > 0:
            self.save_data['balance'] -= total_upkeep
            self.update_money_display()
            self.view_home.refresh_view(self.save_data)
            if hasattr(self, 'console_input'):
                self.console_input.setPlaceholderText(f"Monthly Bill: ${total_upkeep:,} (Tax & Upkeep)")

    def update_date_display(self):
        d = self.current_datetime.strftime("%Y-%m-%d")
        t = self.current_datetime.strftime("%H:%M")
        self.date_lbl.setText(f"📅 {d}\n⏰ {t}")

    def update_money_display(self):
        self.money_lbl.setText(f"${self.save_data.get('balance', 0):,.2f}")

    def save_game_logic(self):
        surname = self.save_data.get('player_surname', 'default')
        file_path = os.path.join(os.path.dirname(__file__), "..", "saves", f"{surname}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, indent=4, ensure_ascii=False)
            msg = QMessageBox(self)
            msg.setWindowTitle("System")
            msg.setText("Game progress saved successfully!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("QLabel{ color: white; }")
            msg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def save_and_exit_logic(self):
        self.save_game_logic()
        self.return_to_menu()

    def return_to_menu(self):
        if self.parent: self.parent.show_main_menu()

    def create_side_menu(self):
        frame = QFrame()
        frame.setFixedWidth(230)
        layout = QVBoxLayout(frame)
        layout.setSpacing(18)
        layout.setContentsMargins(12, 25, 12, 25)
        self.menu_btns = []
        items = [("🏠 HOME", "h"), ("📊 Dashboard", "d"), ("📈 Markets", "m"), ("💼 Portfolio", "p"), ("🏢 Business", "b")]
        for text, key in items:
            btn = QPushButton(text)
            btn.setFixedHeight(65)
            layout.addWidget(btn)
            self.menu_btns.append(btn)
        layout.addStretch()
        return frame

    def apply_theme(self):
        if not self.theme: return
        c = self.theme.get_colors()
        s = f"QFrame {{ background-color: {c['tile_bg']}; border: 1px solid {c['tile_border']}; border-radius: 18px; }}"
        self.header.setStyleSheet(s)
        self.side_menu.setStyleSheet(s)
        
        self.view_home.apply_theme(c)
        self.view_household.apply_theme(c)
        self.view_vehicles.apply_theme(c) # DODANO TEMAT DLA POJAZDÓW
        self.view_system.setStyleSheet("QFrame { background-color: #161616; border: 3px solid #3a96dd; border-radius: 18px; }")
        
        self.player_area.setStyleSheet("border: none; background: transparent;")
        self.money_lbl.setStyleSheet("color: #2ecc71; border: none; font-size: 34px;")
        self.date_lbl.setStyleSheet(f"color: {c['text']}; border: none;")
        
        btn_style = """
            QPushButton {
                background-color: #3a96dd;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #5fb8ff;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #4fb2ff;
            }
            QPushButton:pressed {
                background-color: #2a76ad;
            }
        """
        self.btn_system.setStyleSheet(btn_style)
        self.btn_system.setStyleSheet(btn_style)
        for b in self.time_btns: b.setStyleSheet(btn_style.replace("8px", "5px"))
        for b in self.sys_btns: b.setStyleSheet(btn_style.replace("8px", "12px"))
        
        tile_style = f"QPushButton {{ background-color: #2a2a2a; color: {c['text']}; border: 1px solid #444; border-radius: 12px; text-align: left; padding-left: 20px; font-weight: bold; font-size: 15px; }}"
        for btn in self.menu_btns: btn.setStyleSheet(tile_style)