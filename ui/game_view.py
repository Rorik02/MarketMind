import os
import json
import math
import random
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
from ui.views.markets_view import MarketsView
from ui.views.portfolio_view import PortfolioView
from ui.views.dashboard_view import DashboardView
from ui.views.history_view import HistoryView
from ui.views.bank_view import BankView

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
        
        # Kluczowe: Jeśli historia giełdy jest pusta, wypełnij ją 
        # punktem startowym przed pokazaniem interfejsu
        market_data = self.save_data.get('market_data', {})
        for cat in ['stocks', 'crypto']:
            for symbol, data in market_data.get(cat, {}).items():
                if 'history' not in data or len(data['history']) == 0:
                    data['history'] = [{
                        "date": self.current_datetime.strftime("%Y-%m-%d"),
                        "price": data['current_price']
                    }]

        # Workspace Stack - Zarządzanie widokami
        self.workspace_stack = QStackedWidget()
        
        # Inicjalizacja widoków
        self.view_home = HomeView(self, self.theme, self.save_data)
        self.view_dashboard = self.create_placeholder_view("📊 Dashboard", "Financial statistics and charts.")
        self.view_markets = MarketsView(self)
        self.view_portfolio = self.create_placeholder_view("💼 Portfolio", "Your assets and investments.")
        self.view_business = self.create_placeholder_view("🏢 Business", "Companies and management.")
        self.view_system = self.create_system_menu_view()
        self.view_household = HouseholdView(self, self.theme, self.save_data)
        self.view_vehicles = VehicleView(self, self.theme, self.save_data)
        self.view_valuables = ValuablesView(self, self.theme, self.save_data)
        self.view_employment = EmploymentView(self, self.theme, self.save_data)
        self.view_portfolio = PortfolioView(self)
        self.view_dashboard = DashboardView(self)
        self.view_history = HistoryView(self)
        self.view_bank = BankView(self, self.theme, self.save_data)

        self.btn_bank.setCursor(Qt.CursorShape.PointingHandCursor)
        
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
        self.workspace_stack.addWidget(self.view_history)   #10
        self.workspace_stack.addWidget(self.view_bank)      #11

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
        self.setup_initial_state(self.save_data)

    def setup_initial_state(self, save_data):
        """Inicjalizuje historię i odświeża widok giełdy."""
        self.save_data = save_data
        market_data = self.save_data.get('market_data', {})
        for cat in ['stocks', 'crypto']:
            items = market_data.get(cat, {})
            for symbol, data in items.items():
                # Tworzymy startowy punkt historii, jeśli go brakuje
                if 'history' not in data or not data['history']:
                    data['history'] = [{
                        "date": self.current_datetime.strftime("%Y-%m-%d"),
                        "price": data['current_price']
                    }]
        
        # Teraz view_markets na pewno już istnieje
        if hasattr(self, 'view_markets'):
            self.view_markets.refresh_view(self.save_data)

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
        old_date = self.current_datetime

        if self.save_data.get('balance', 0) < 0:
            msg = QMessageBox(self)
            msg.setWindowTitle("Financial Alert")
            msg.setText("<b>YOUR ACCOUNT IS FROZEN!</b><br>You are in debt. Sell assets or take a loan to continue.")
            msg.addButton("Go to Bank", QMessageBox.ButtonRole.AcceptRole).clicked.connect(lambda: self.switch_view(11))
            msg.addButton("Sell Assets", QMessageBox.ButtonRole.AcceptRole).clicked.connect(lambda: self.switch_view(3))
            msg.exec()
            return
        
        # DODAJEMY CZAS TYLKO RAZ
        self.current_datetime += timedelta(hours=hours)
        
        # --- NOWA LOGIKA RYNKOWA ---
        # Sprawdzamy, czy minęła przynajmniej jedna doba
        if self.current_datetime.date() > old_date.date():
            days_passed = (self.current_datetime.date() - old_date.date()).days
            for _ in range(days_passed):
                self.simulate_market_movement()
        # ---------------------------

        # Aktualizujemy datę w save_data dla widoku profilu
        self.save_data['current_game_date'] = self.current_datetime.strftime("%Y-%m-%d")
        self.save_data['created'] = self.current_datetime.strftime("%Y-%m-%d %H:%M")
        
        self.update_date_display()

        # Sprawdzamy szansę na śmierć tylko raz
        if self.current_datetime.date() > old_date.date():
            if self.check_death_chance():
                return 

        # Logika kursów edukacyjnych
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

        # ODŚWIEŻANIE AKTYWNEGO WIDOKU
        current_idx = self.workspace_stack.currentIndex()
        if current_idx == 0:
            self.view_home.refresh_view(self.save_data)
        elif current_idx == 2: # Markets
            self.view_markets.refresh_view(self.save_data)
        elif current_idx == 3: # Portfolio
            self.view_portfolio.refresh_view(self.save_data)
        elif current_idx == 9:
            self.view_employment.refresh_tabs()
        elif current_idx == 10: # Historia
            self.view_history.refresh_view(self.save_data)

        # Finanse miesięczne
        if hours >= 720:
            self.process_monthly_finances()

    def process_monthly_finances(self):
        """Główna metoda rozliczająca miesiąc: pensje, dywidendy, koszty i POŻYCZKI."""
        # --- 1. PENSJA I UTRZYMANIE (Co miesiąc) ---
        job_id = self.save_data.get('current_job')
        salary = 0
        if job_id:
            self.save_data['job_months'] = self.save_data.get('job_months', 0) + 1
            salary = self.calculate_salary_with_milestones(job_id, self.save_data['job_months'])

        total_upkeep = self.calculate_total_property_upkeep()

        total_loan_costs = 0
        loans = self.save_data.get('active_loans', [])
        
       # --- 2. OBSŁUGA POŻYCZEK Z KARENCJĄ ---
        total_loan_costs = 0
        loans = self.save_data.get('active_loans', [])
        
        for loan in loans[:]:
            # Sprawdzenie karencji: jeśli pożyczka jest nowa, pomijamy spłatę w tym cyklu
            if loan.get('is_new', False):
                loan['is_new'] = False # Zdejmujemy flagę, spłata zacznie się w przyszłym miesiącu
                continue

            loan['remaining_months'] -= 1
            loan['paid_amount'] += loan['monthly_rate']
            total_loan_costs += loan['monthly_rate']
            
            if loan['remaining_months'] <= 0:
                loans.remove(loan)
                QMessageBox.information(self, "Bank", f"Twoja pożyczka ({loan['type']}) została spłacona!")

        # --- 3. DYWIDENDY KWARTALNE (Marzec, Czerwiec, Wrzesień, Grudzień) ---
        total_dividends = 0
        current_month = self.current_datetime.month
        
        if current_month in [3, 6, 9, 12]:
            portfolio = self.save_data.get('portfolio', {})
            market_data = self.save_data.get('market_data', {})
            for symbol, p_data in portfolio.get('stocks', {}).items():
                amount = p_data.get('amount', 0)
                if amount > 0:
                    m_info = market_data.get('stocks', {}).get(symbol, {})
                    current_price = m_info.get('current_price', 0)
                    div_rate = m_info.get('dividend_yield', 0) 
                    total_dividends += (amount * current_price * div_rate)

        # --- 4. LOGOWANIE DO HISTORII (📜) ---
        if salary > 0:
            self.log_transaction("Praca", f"Pensja: {self.save_data.get('current_title', 'Pracownik')}", salary)
        
        if total_dividends > 0:
            self.log_transaction("Giełda", f"Dywidenda kwartalna ({current_month})", total_dividends)

        if total_upkeep > 0:
            self.log_transaction("Opłaty", "Utrzymanie nieruchomości", -total_upkeep)
            
        if total_loan_costs > 0:
            # Logujemy ratę pożyczki jako wydatek bankowy
            self.log_transaction("Bank", "Automatyczna rata pożyczki", -total_loan_costs)

        # --- 5. FINALNA AKTUALIZACJA BALANSU ---
        # Uwzględniamy dochody i wszystkie koszty, w tym raty
        self.save_data['balance'] += (salary + total_dividends - total_upkeep - total_loan_costs)

        # --- 6. ODŚWIEŻENIE INTERFEJSU ---
        self.update_money_display()
        if hasattr(self, 'view_home'):
            self.view_home.refresh_view(self.save_data)
        
        if self.workspace_stack.currentIndex() == 10:
            self.view_history.refresh_view(self.save_data)
            
        # Odśwież widok banku, jeśli jest otwarty, aby zaktualizować paski postępu
        if hasattr(self, 'view_bank'):
            self.view_bank.refresh_view(self.save_data)

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
            
        self.player_info = QLabel(
            f"<b>{self.save_data.get('player_name')}</b><br>"
            f"<font color='#aaaaaa'>{self.save_data.get('current_title', 'Unemployed')}</font>"
        )
        p_layout.addWidget(self.avatar_lbl)
        p_layout.addWidget(self.player_info)

        self.btn_bank = QPushButton("🏦 BANK")
        self.btn_bank.setFixedSize(80, 45)
        self.btn_bank.setStyleSheet("background: #2c3e50; color: #ecf0f1; border-radius: 22px; font-weight: bold;")
        self.btn_bank.clicked.connect(lambda: self.switch_view(11))
        
        # Wstawiamy do layoutu nagłówka przed pieniędzmi
        layout.addWidget(self.btn_bank)

        # LICZNIK PIENIĘDZY
        self.money_lbl = QLabel(f"${self.save_data.get('balance', 0):,.2f}")
        self.money_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.money_lbl.setStyleSheet("color: #2ecc71; border: none; background: transparent;")
        self.money_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- NOWY PRZYCISK HISTORII (📜) OBOK KASY ---
        self.btn_history = QPushButton("📜")
        self.btn_history.setFixedSize(45, 45)
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_history.setToolTip("Otwórz historię transakcji")
        self.btn_history.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 2px solid #333;
                border-radius: 22px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #3a96dd;
                border-color: #3a96dd;
            }
        """)
        
        self.btn_history.clicked.connect(lambda: self.switch_view(10))

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
                    background-color: #3a3a3a; color: white; border: none;
                    border-radius: 5px; font-weight: bold; font-size: 13px;
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

        # SKŁADANIE LAYOUTU (Ważna kolejność!)
        layout.addWidget(self.player_area, 0)
        layout.addStretch(1)
        layout.insertWidget(2, self.btn_bank)
        layout.addWidget(self.money_lbl)
        layout.addWidget(self.btn_history) # Wrzucamy ikonę zaraz za kasą
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
        from datetime import datetime # Import potrzebny do obliczenia wieku
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

        # --- TWOJA NOWA KOMENDA TESTOWA ---
        elif command == "kill":
            try:
                dob_str = self.save_data.get('date_of_birth', '1990-01-01')
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
                age = self.current_datetime.year - dob.year
                
                # Wywołujemy funkcję raportu, którą wcześniej przygotowaliśmy
                self.trigger_end_game(age)
                return f"Szymon died for science at age {age}. Report generated."
            except Exception as e:
                return f"Error triggering death: {str(e)}"

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
            # i=2 to indeks zakładki Markets w Twoim workspace_stack
            btn.clicked.connect(lambda checked, index=i: self.switch_view(index))

    def switch_view(self, index):
        self.workspace_stack.setCurrentIndex(index)
        if index == 2:
            self.view_markets.refresh_view(self.save_data)
        if index == 3: # Zakładka Portfolio
            self.view_portfolio.refresh_view(self.save_data)
        if index == 1:  
            self.view_dashboard.refresh_view(self.save_data)
        if index == 10: # To musi tu być!
            self.view_history.refresh_view(self.save_data)
        if index == 11:
            self.view_bank.refresh_view(self.save_data)
    
    def switch_workspace(self, index):
        """Przełącza widok i odświeża dane jeśli to konieczne."""
        self.workspace_stack.setCurrentIndex(index)
        
        if index == 2:
            self.view_markets.refresh_view(self.save_data)

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

        # --- POPRAWIONA STYLIZACJA OKIEN KOMUNIKATÓW ---
        msg_style = f"""
            QMessageBox {{
                background-color: #1a1a1a;
                border: 2px solid #3a96dd;
                border-radius: 10px;
            }}
            QMessageBox QLabel {{
                color: white;
                font-weight: bold;
                padding: 15px;
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background-color: #2a2a2a;      /* Ciemne tło jak w menu */
                color: #3a96dd;                 /* Niebieski tekst */
                border: 2px solid #3a96dd;      /* WYRAŹNA NIEBIESKA RAMKA */
                border-radius: 8px;
                padding: 8px 25px;
                min-width: 100px;
                font-weight: bold;
                font-size: 14px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #3a96dd;      /* Po najechaniu wypełnia się */
                color: white;
            }}
        """
        self.setStyleSheet(self.styleSheet() + msg_style)

    def check_death_chance(self):
        """Sprawdza szansę na zgon na podstawie aktualnego wieku."""
        # Pobieramy datę urodzenia z zapisu
        dob_str = self.save_data.get('date_of_birth', '1990-01-01')
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        
        # Obliczamy wiek w aktualnym czasie gry
        age = self.current_datetime.year - dob.year
        
        # Twoja formuła: 18 lat -> ~0%, 100 lat -> ~99%
        base = 1.12
        annual_chance = (pow(base, age - 18) / pow(base, 100 - 18)) * 100
        
        # Ponieważ sprawdzamy to często, dzielimy szansę roczną przez 365 dni
        import random
        daily_chance = annual_chance / 365
        if random.random() * 100 < daily_chance:
            self.trigger_end_game(age)
            return True
        return False

    def trigger_end_game(self, age):
        """Summarizes estate using the exact logic from update_valuables_status."""
        try:
            cash = self.save_data.get('balance', 0)
            total_prestige = self.save_data.get('prestige', 0)
            
            # 1. Property Valuation
            props_val = 0
            owned_props = self.save_data.get('owned_properties', [])
            import os, json
            props_path = os.path.join(os.path.dirname(__file__), "..", "data", "properties.json")
            if os.path.exists(props_path):
                with open(props_path, 'r', encoding='utf-8') as f:
                    props_data = json.load(f)
                    for p in props_data:
                        if p['id'] in owned_props: props_val += p.get('price', 0)


            # 2. Vehicle Valuation
            vehs_val = 0
            owned_vehs = self.save_data.get('owned_vehicles', [])
            vehs_path = os.path.join(os.path.dirname(__file__), "..", "data", "vehicles.json")
            if os.path.exists(vehs_path):
                with open(vehs_path, 'r', encoding='utf-8') as f:
                    vehs_data = json.load(f)
                    for v in vehs_data:
                        if v['id'] in owned_vehs: vehs_val += v.get('price', 0)

            # 3. FIX: Valuables Valuation (Using your specific logic)
            items_val = 0
            # Twoja metoda korzysta z klucza 'owned_valuables'
            owned_ids = self.save_data.get('owned_valuables', [])
            valuables_path = os.path.join(os.path.dirname(__file__), "..", "data", "valuables.json")
            
            if os.path.exists(valuables_path):
                with open(valuables_path, 'r', encoding='utf-8') as f:
                    items_db = json.load(f)
                    for item in items_db:
                        if item['id'] in owned_ids:
                            # Twoja funkcja szuka pola 'price'
                            items_val += item.get('price', 0)

            total_net_worth = cash + props_val + vehs_val + items_val

            # English Report HTML
            report = (
                f"<div style='color: white;'>"
                f"<h2 style='color: #e74c3c; text-align: center;'>GAME OVER</h2>"
                f"<p style='font-size: 14px; text-align: center;'>Szymon Rorat passed away at the age of <b>{age}</b>.</p>"
                f"<hr>"
                f"<p><b>ESTATE SUMMARY:</b></p>"
                f"💰 Cash: ${cash:,.2f}<br>"
                f"🏠 Real Estate: ${props_val:,.2f}<br>"
                f"🏎️ Vehicles: ${vehs_val:,.2f}<br>"
                f"💎 Valuables: ${items_val:,.2f}<br><br>"
                f"⭐ <b>Final Prestige: {total_prestige:,}</b><br><br>"
                f"<div style='background: #2a2a2a; padding: 12px; border: 2px solid #3a96dd; text-align: center;'>"
                f"<span style='font-size: 18px; color: #3a96dd; font-weight: bold;'>"
                f"FINAL NET WORTH: ${total_net_worth:,.2f}</span>"
                f"</div></div>"
            )

            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("The Final Chapter")
            msg.setText(report)
            msg.exec()
            
            if hasattr(self, 'parent') and self.parent:
                self.parent.show_main_menu()
            else:
                self.close()
                
        except Exception as e:
            print(f"DEBUG Error: {str(e)}")
    
    def simulate_market_movement(self):
        """Symuluje zmianę cen na giełdzie przy każdym skoku czasu."""
        market_data = self.save_data.get('market_data', {})
        
        for category in ['stocks', 'crypto']:
            items = market_data.get(category, {})
            for symbol, data in items.items():
                # 1. Oblicz nową cenę (losowa fluktuacja)
                volatility = 0.02 if category == 'stocks' else 0.05
                change = 1 + random.uniform(-volatility, volatility)
                data['current_price'] = round(data['current_price'] * change, 2)

                # 2. ZABEZPIECZENIE: Inicjalizuj listę history, jeśli jej brakuje
                if 'history' not in data or not isinstance(data['history'], list):
                    data['history'] = []

                # 3. Dodaj nowy punkt do historii
                data['history'].append({
                    "date": self.current_datetime.strftime("%Y-%m-%d"),
                    "price": data['current_price']
                })

                # 4. Ogranicz historię do ostatnich 30 wpisów, by nie zapchać RAMu
                if len(data['history']) > 30:
                    data['history'].pop(0)

    def log_transaction(self, category, description, amount):
        # Upewniamy się, że klucz istnieje w słowniku zapisu
        if 'transaction_history' not in self.save_data:
            self.save_data['transaction_history'] = []
            
        new_entry = {
            "date": self.current_datetime.strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "description": description,
            "amount": float(amount)
        }
        
        # Wstawiamy do listy
        self.save_data['transaction_history'].insert(0, new_entry)
        
        # WYMUSZENIE: Jeśli używasz wielu widoków, upewnij się, że 
        # HistoryView dostanie informację o nowej liście
        if hasattr(self, 'view_history'):
            self.view_history.history_data = self.save_data['transaction_history']

    def show_bankruptcy_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("BANKRUPTCY!")
        msg.setText("<b>You have run out of money!</b><br>To continue, you must settle your debts.")
        
        btn_bank = msg.addButton("Go to Bank", QMessageBox.ButtonRole.AcceptRole)
        btn_portfolio = msg.addButton("Sell Assets", QMessageBox.ButtonRole.AcceptRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_bank:
            self.switch_view(11) # Załóżmy, że BankView to indeks 11
        else:
            self.switch_view(3) # Portfolio to indeks 3