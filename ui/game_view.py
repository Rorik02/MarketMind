import os
import json
import math
import random
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QFrame, QPushButton, QStackedWidget, QMessageBox, QLineEdit,)
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QTimer

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
from utils.event_manager import EventManager
from utils.achievement_manager import AchievementManager
from ui.views.achievements_view import AchievementsView
from ui.widgets.toast import AchievementToast


class GameView(QWidget):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent = parent
        self.toast_queue = []
        self.is_toast_showing = False
        
        self.theme = theme 
        self.save_data = save_data or {}
        self.time_btns = [] 
        
        self.event_manager = EventManager()
        
        date_str = self.save_data.get('created', '2026-01-14 00:00')
        self.current_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        
        self.header = self.create_header()
        
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(20)
        self.side_menu = self.create_side_menu()

        self.workspace_stack = QStackedWidget()

        self.event_cooldown_days = 0
        
        self.view_home = HomeView(self, self.theme, self.save_data)
        self.view_markets = MarketsView(self)
        self.view_portfolio = PortfolioView(self)
        self.view_dashboard = DashboardView(self)
        self.view_history = HistoryView(self)
        self.view_bank = BankView(self, self.theme, self.save_data)
        self.view_system = self.create_system_menu_view()
        self.view_household = HouseholdView(self, self.theme, self.save_data)
        self.view_vehicles = VehicleView(self, self.theme, self.save_data)
        self.view_valuables = ValuablesView(self, self.theme, self.save_data)
        self.view_employment = EmploymentView(self, self.theme, self.save_data)
        self.view_achievements = AchievementsView(self, self.theme, self.save_data) 

        self.workspace_stack.addWidget(self.view_home)      # 0
        self.workspace_stack.addWidget(self.view_dashboard) # 1
        self.workspace_stack.addWidget(self.view_markets)   # 2
        self.workspace_stack.addWidget(self.view_portfolio) # 3
        self.workspace_stack.addWidget(self.create_placeholder_view("🏢 Business", "Coming soon")) # 4
        self.workspace_stack.addWidget(self.view_system)    # 5
        self.workspace_stack.addWidget(self.view_household) # 6
        self.workspace_stack.addWidget(self.view_vehicles)  # 7
        self.workspace_stack.addWidget(self.view_valuables) # 8
        self.workspace_stack.addWidget(self.view_employment)# 9
        self.workspace_stack.addWidget(self.view_history)   # 10
        self.workspace_stack.addWidget(self.view_bank)      # 11
        self.workspace_stack.addWidget(self.view_achievements) # 12

        self.main_layout.addWidget(self.header)
        self.content_layout.addWidget(self.side_menu, 1)
        self.content_layout.addWidget(self.workspace_stack, 4)
        self.main_layout.addLayout(self.content_layout)

        self.connect_menu_logic()
        self.setup_initial_state(self.save_data)
        
        self.apply_theme()
        self.save_data['max_prestige'] = self.calculate_total_game_prestige()
        self.achievement_manager = AchievementManager(self)


    def setup_initial_state(self, save_data):
        """Inicjalizuje historię i odświeża widok giełdy."""
        self.save_data = save_data
        market_data = self.save_data.get('market_data', {})
        for cat in ['stocks', 'crypto']:
            items = market_data.get(cat, {})
            for symbol, data in items.items():
            
                if 'history' not in data or not data['history']:
                    data['history'] = [{
                        "date": self.current_datetime.strftime("%Y-%m-%d"),
                        "price": data['current_price']
                    }]
        
        if hasattr(self, 'view_markets'):
            self.view_markets.refresh_view(self.save_data)

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

        days_to_subtract = hours / 24
        if not hasattr(self, 'event_cooldown_days'):
            self.event_cooldown_days = 0
            
        if self.event_cooldown_days > 0:
            self.event_cooldown_days -= days_to_subtract
            if self.event_cooldown_days < 0: self.event_cooldown_days = 0

        if hours >= 24:
            days_to_jump = hours // 24
            for _ in range(days_to_jump):
                self.current_datetime += timedelta(days=1)
                
                self.event_manager.process_day()
                self.simulate_market_movement()
                self.check_death_chance()
        else:
            self.current_datetime += timedelta(hours=hours)

        self.save_data['current_game_date'] = self.current_datetime.strftime("%Y-%m-%d")
        self.save_data['created'] = self.current_datetime.strftime("%Y-%m-%d %H:%M")
        self.update_date_display()

        if self.save_data.get('active_course'):
            course = self.save_data['active_course']
            course['remaining_hours'] -= hours
            if course['remaining_hours'] <= 0:
                if 'completed_courses' not in self.save_data: self.save_data['completed_courses'] = []
                if course['id'] not in self.save_data['completed_courses']:
                    self.save_data['completed_courses'].append(course['id'])
                self.save_data['active_course'] = None
                QMessageBox.information(self, "Education", f"Course Finished: {course['name']}")

        if hours >= 720:
            self.process_monthly_finances()
            
            if not self.event_manager.active_events and self.event_cooldown_days <= 0:
                if random.random() < 0.15:
                    events = self.event_manager.events_db
                    
                    if events:
                        weights = [e.get('weight', 1) for e in events]
                        
                        random_event = random.choices(events, weights=weights, k=1)[0]
                        
                        self.event_manager.trigger_event_by_id(random_event['id'])
                        
                        self.event_cooldown_days = 365
                        print(f"DEBUG: Wylosowano event: {random_event['name']} (Waga: {random_event.get('weight', 1)})")

        self.achievement_manager.check_all()

        self.update_news_feed()
        self.refresh_active_view()

    def refresh_active_view(self):
        """Pomocnicza metoda do odświeżania aktualnego okna."""
        current_idx = self.workspace_stack.currentIndex()
        views = {0: self.view_home, 2: self.view_markets, 3: self.view_portfolio, 
                 9: self.view_employment, 10: self.view_history}
        if current_idx in views:
            if current_idx == 9: views[current_idx].refresh_tabs()
            else: views[current_idx].refresh_view(self.save_data)

    def process_monthly_finances(self):
        """Główna metoda rozliczająca miesiąc: pensje, dywidendy, koszty i POŻYCZKI."""
        job_id = self.save_data.get('current_job')
        salary = 0
        if job_id:
            self.save_data['job_months'] = self.save_data.get('job_months', 0) + 1
            salary = self.calculate_salary_with_milestones(job_id, self.save_data['job_months'])

        total_upkeep = self.calculate_total_property_upkeep()

        total_loan_costs = 0
        loans = self.save_data.get('active_loans', [])
        
        total_loan_costs = 0
        loans = self.save_data.get('active_loans', [])
        
        for loan in loans[:]:
            if loan.get('is_new', False):
                loan['is_new'] = False 
                continue

            loan['remaining_months'] -= 1
            loan['paid_amount'] += loan['monthly_rate']
            total_loan_costs += loan['monthly_rate']
            
            if loan['remaining_months'] <= 0:
                loans.remove(loan)
                QMessageBox.information(self, "Bank", f"Twoja pożyczka ({loan['type']}) została spłacona!")

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

        if salary > 0:
            self.log_transaction("Praca", f"Pensja: {self.save_data.get('current_title', 'Pracownik')}", salary)
        
        if total_dividends > 0:
            self.log_transaction("Giełda", f"Dywidenda kwartalna ({current_month})", total_dividends)

        if total_upkeep > 0:
            self.log_transaction("Opłaty", "Utrzymanie nieruchomości", -total_upkeep)
            
        if total_loan_costs > 0:
            self.log_transaction("Bank", "Automatyczna rata pożyczki", -total_loan_costs)

        self.save_data['balance'] += (salary + total_dividends - total_upkeep - total_loan_costs)

        self.update_money_display()
        if hasattr(self, 'view_home'):
            self.view_home.refresh_view(self.save_data)
        
        if self.workspace_stack.currentIndex() == 10:
            self.view_history.refresh_view(self.save_data)
            
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
            
        self.player_info = QLabel(f"<b>{self.save_data.get('player_name')}</b><br><font color='#aaaaaa'>{self.save_data.get('current_title', 'Unemployed')}</font>")
        p_layout.addWidget(self.avatar_lbl)
        p_layout.addWidget(self.player_info)

        center_group = QWidget()
        finance_layout = QHBoxLayout(center_group)
        finance_layout.setContentsMargins(0, 0, 0, 0)
        finance_layout.setSpacing(15)
        finance_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_news = QPushButton("Market is stable")
        self.btn_news.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_news.setStyleSheet("color: #aaaaaa; font-style: italic; border: none; background: transparent; font-size: 13px;")
        self.btn_news.clicked.connect(self.show_event_details)
        
        self.btn_bank = QPushButton("🏦 BANK")
        self.btn_bank.setFixedSize(80, 45)
        self.btn_bank.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bank.setStyleSheet("background: #2c3e50; color: #ecf0f1; border-radius: 22px; font-weight: bold;")
        self.btn_bank.clicked.connect(lambda: self.switch_view(11))
        
        self.money_lbl = QLabel(f"${self.save_data.get('balance', 0):,.2f}")
        self.money_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.money_lbl.setStyleSheet("color: #2ecc71; border: none; background: transparent;")
        
        self.btn_history = QPushButton("📜")
        self.btn_history.setFixedSize(45, 45)
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_history.setStyleSheet("background-color: #2a2a2a; color: white; border-radius: 22px; font-size: 20px;")
        self.btn_history.clicked.connect(lambda: self.switch_view(10))

        finance_layout.addWidget(self.btn_news)
        finance_layout.addWidget(self.btn_bank)
        finance_layout.addWidget(self.money_lbl)
        finance_layout.addWidget(self.btn_history)

        self.right_container = QWidget()
        r_layout = QHBoxLayout(self.right_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(10)

        self.date_container = QFrame()
        self.date_container.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        d_inner_layout = QVBoxLayout(self.date_container)
        d_inner_layout.setContentsMargins(8, 2, 8, 2)
        d_inner_layout.setSpacing(0)
        
        self.date_lbl = QLabel()
        self.date_lbl.setStyleSheet("border: none; background: transparent; color: white; font-weight: bold;")
        self.update_date_display()
        d_inner_layout.addWidget(self.date_lbl)
        r_layout.addWidget(self.date_container)
        
        self.time_btns = []
        for label, hours in [("+1h", 1), ("+1d", 24), ("+1w", 168), ("+1m", 720)]:
            btn = QPushButton(label)
            btn.setFixedSize(60, 38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: #2a2a2a; color: white; border-radius: 5px; }
                QPushButton:hover { background-color: #3a3a3a; }
            """)
            btn.clicked.connect(lambda ch, h=hours: self.advance_time(h))
            r_layout.addWidget(btn)
            self.time_btns.append(btn)

        self.btn_system = QPushButton("⚙️ SYSTEM")
        self.btn_system.setFixedSize(110, 40)
        self.btn_system.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_system.setStyleSheet("""
            QPushButton { background-color: #3a96dd; color: white; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #4aa6ed; }
        """)
        self.btn_system.clicked.connect(self.toggle_system_menu)
        r_layout.addWidget(self.btn_system)

        layout.addWidget(self.player_area, 0)
        layout.addStretch(1)
        layout.addWidget(center_group, 0)
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
        command = parts[0].lower()
        args = parts[1:]

        if command == "money" and len(args) > 0:
            try:
                amount = float(args[0])
                self.save_data['balance'] += amount
                self.update_money_display()
                return f"Added ${amount:,.2f}"
            except: return "Error"

        elif command == "event" and len(args) > 0:
            try:
                event_id = args[0].upper()
                result = self.event_manager.trigger_event_by_id(event_id)
                self.update_news_feed()
                return result
            except Exception as e:
                return f"Event Error: {str(e)}"

        elif command == "prestige" and len(args) > 0:
            try:
                amount = int(args[0])
                self.save_data['prestige_bonus'] = self.save_data.get('prestige_bonus', 0) + amount
                self.view_home.refresh_view(self.save_data)
                return f"Added {amount} prestige bonus"
            except: return "Error"

        elif command == "kill":
            try:
                dob_str = self.save_data.get('date_of_birth', '1990-01-01')
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
                age = self.current_datetime.year - dob.year
                
                self.trigger_end_game(age)
                return f"Szymon died for science at age {age}. Report generated."
            except Exception as e:
                return f"Error triggering death: {str(e)}"

        elif command == "test_luck":
            events = self.event_manager.events_db
            weights = [e.get('weight', 1) for e in events]
            total = sum(weights)
            top_events = sorted(events, key=lambda x: x.get('weight', 1), reverse=True)[:3]
            res = "Top Odds: " + ", ".join([f"{e['name']} ({e['weight']/total*100:.1f}%)" for e in top_events])
            return res

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
        items = ["🏠 HOME", "📊 Dashboard", "📈 Markets", "💼 Portfolio"]
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
            btn.clicked.connect(lambda checked, index=i: self.switch_view(index))

    def switch_view(self, index):
        self.workspace_stack.setCurrentIndex(index)
        if index == 2:
            self.view_markets.refresh_view(self.save_data)
        if index == 3:
            self.view_portfolio.refresh_view(self.save_data)
        if index == 1:  
            self.view_dashboard.refresh_view(self.save_data)
        if index == 10: 
            self.view_history.refresh_view(self.save_data)
        if index == 11:
            self.view_bank.refresh_view(self.save_data)
        if index == 12:
            self.view_achievements.refresh_view(self.save_data) #
    
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
        dob_str = self.save_data.get('date_of_birth', '1990-01-01')
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        
        age = self.current_datetime.year - dob.year
        
        base = 1.12
        annual_chance = (pow(base, age - 18) / pow(base, 100 - 18)) * 100
        
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
            
            props_val = 0
            owned_props = self.save_data.get('owned_properties', [])
            import os, json
            props_path = os.path.join(os.path.dirname(__file__), "..", "data", "properties.json")
            if os.path.exists(props_path):
                with open(props_path, 'r', encoding='utf-8') as f:
                    props_data = json.load(f)
                    for p in props_data:
                        if p['id'] in owned_props: props_val += p.get('price', 0)


            vehs_val = 0
            owned_vehs = self.save_data.get('owned_vehicles', [])
            vehs_path = os.path.join(os.path.dirname(__file__), "..", "data", "vehicles.json")
            if os.path.exists(vehs_path):
                with open(vehs_path, 'r', encoding='utf-8') as f:
                    vehs_data = json.load(f)
                    for v in vehs_data:
                        if v['id'] in owned_vehs: vehs_val += v.get('price', 0)

            items_val = 0
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
        """Symuluje zmianę cen na giełdzie przy każdym skoku czasu z uwzględnieniem wydarzeń."""
        market_data = self.save_data.get('market_data', {})
        
        for category in ['stocks', 'crypto']:
            items = market_data.get(category, {})
            for symbol, data in items.items():
                sector = data.get('category', category).lower() 
                event_modifier = self.event_manager.get_modifier_for_symbol(symbol, sector)

                volatility = 0.02 if category == 'stocks' else 0.05
                base_change = 1 + random.uniform(-volatility, volatility)
                
                total_change = base_change * event_modifier
                
                data['current_price'] = round(data['current_price'] * total_change, 2)

                if 'history' not in data or not isinstance(data['history'], list):
                    data['history'] = []

                data['history'].append({
                    "date": self.current_datetime.strftime("%Y-%m-%d"),
                    "price": data['current_price']
                })

                if len(data['history']) > 30:
                    data['history'].pop(0)

    def log_transaction(self, category, description, amount):
        if 'transaction_history' not in self.save_data:
            self.save_data['transaction_history'] = []
            
        new_entry = {
            "date": self.current_datetime.strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "description": description,
            "amount": float(amount)
        }
        
        self.save_data['transaction_history'].insert(0, new_entry)
        
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
            self.switch_view(11)
        else:
            self.switch_view(3)

    def fix_existing_dividends(self):
        """Naprawia zepsute dywidendy wczytane z zapisu (np. 143.0 -> 0.0143)."""
        market_data = self.save_data.get('market_data', {})
        count = 0
        for cat in ['stocks', 'crypto']:
            for symbol, data in market_data.get(cat, {}).items():
                div = data.get('dividend_yield', 0)
                if div > 0.05:
                    data['dividend_yield'] = round(div / 100, 6)
                    count += 1
        if count > 0:
            print(f"--- SYSTEM: Naprawiono {count} nierealnych dywidend! ---")
        
    def show_event_details(self):
        """Wyświetla szczegółowy raport o wpływie wydarzenia na konkretne aktywa."""
        active = self.event_manager.active_events
        if not active:
            return

        ev = active[-1]['event']
        impact_val = ev.get('impact', 1.0)
        impact_text = "Positively" if impact_val > 1.0 else "Negatively"
        color = "#2ecc71" if impact_val > 1.0 else "#e74c3c"
        
        target_type = ev.get('target_type')
        target_id = ev.get('target_id', '').upper()
        
        affected_info = ""
        if target_type == "global":
            affected_info = "This is a <b>Global Event</b> affecting every single asset on the market."
        elif target_type == "sector":
            affected_info = f"This event specifically targets the <b>{target_id}</b> sector."
        elif target_type == "single":
            affected_info = f"This is a company-specific event targeting <b>{target_id}</b>."

        msg = QMessageBox(self)
        msg.setWindowTitle("🚨 MARKET ANALYSIS")
        
        html_content = f"""
            <div style='min-width: 350px; font-family: Arial;'>
                <h2 style='color: {color}; margin-bottom: 0;'>{ev['name']}</h2>
                <p style='color: #aaaaaa; font-style: italic; margin-top: 5px;'>News Report</p>
                <p style='font-size: 14px; line-height: 1.4;'>{ev.get('description', '')}</p>
                <hr style='border: 0; border-top: 1px solid #444;'>
                <p style='font-size: 13px;'>📍 <b>Affected Assets:</b> {affected_info}</p>
                <p style='font-size: 13px;'>📉 <b>Trend:</b> <span style='color: {color}; font-weight: bold;'>{impact_text}</span></p>
                <p style='font-size: 11px; color: #777; margin-top: 10px;'>
                    Analyst note: This event will remain active for {active[-1]['remaining']} more days.
                </p>
            </div>
        """
        
        msg.setText(html_content)
        msg.exec()

    def update_news_feed(self):
        active = self.event_manager.active_events
        
        if not active:
            self.btn_news.setText("Market is stable")
            self.btn_news.setStyleSheet("color: #aaaaaa; font-style: italic; border: none; background: transparent; font-size: 13px;")
            return

        ev_data = active[-1]
        ev = ev_data['event']
        
        print(f"DEBUG: Aktualizacja newsów. Aktywny event: {ev['name']}")

        self.btn_news.setText(f"(NEWS) {ev['name']}")
        self.btn_news.setStyleSheet("""
            QPushButton {
                color: #2ecc71; 
                font-weight: bold; 
                border: 1px solid #2ecc71; 
                border-radius: 5px; 
                padding: 4px 10px; 
                background: rgba(46, 204, 113, 0.1);
                font-size: 13px;
            }
        """)

    def calculate_total_game_prestige(self):
        total = 0
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        for file in ["properties.json", "vehicles.json", "valuables.json"]:
            path = os.path.join(data_dir, file)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                    for item in items:
                        total += item.get('prestige', 0)
        return total
    
    def show_achievement_toast(self, ach_id):
        self.toast_queue.append(ach_id)
        self.process_toast_queue()

    def process_toast_queue(self):
        if not self.toast_queue or self.is_toast_showing:
            return

        self.is_toast_showing = True
        ach_id = self.toast_queue.pop(0)

        defs = getattr(self.achievement_manager, 'achievements', [])
        ach_data = next((a for a in defs if a['id'] == ach_id), None)
        
        if ach_data:
            toast = AchievementToast(self, ach_data['name'], ach_data['description'])
            toast.raise_()
            toast.show()

            QTimer.singleShot(5500, self.reset_toast_flag)

    def reset_toast_flag(self):
        self.is_toast_showing = False
        self.process_toast_queue()