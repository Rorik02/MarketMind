import json
import os
from datetime import datetime

class AchievementManager:
    def __init__(self, game_view):
        self.gv = game_view
        self.achievements = self.load_achievement_definitions()

    def load_achievement_definitions(self):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "achievements.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f).get('achievements', [])
        except Exception as e:
            print(f"DEBUG: Nie można wczytać definicji osiągnięć: {e}")
            return []

    def check_all(self):
        """Główna pętla sprawdzająca warunki."""
        save = self.gv.save_data
        if 'unlocked_achievements' not in save:
            save['unlocked_achievements'] = []
        
        unlocked = save['unlocked_achievements']

        portfolio_val = self.calculate_portfolio_value()
        net_worth = save.get('balance', 0) + portfolio_val
        owned_v = save.get('owned_vehicles', [])
        owned_val = save.get('owned_valuables', [])
        owned_props = save.get('owned_properties', [])
        completed_courses = save.get('completed_courses', [])
        current_prestige = save.get('prestige', 0)
        age = self.calculate_age()
        active_event_ids = [e['event']['id'] for e in self.gv.event_manager.active_events]


        if net_worth >= 250_000_000_000 and "be_elon" not in unlocked: self.unlock("be_elon")
        if net_worth >= 10_000_000 and "decamillionaire" not in unlocked: self.unlock("decamillionaire")
        if net_worth >= 1_000_000 and "millionaire" not in unlocked: self.unlock("millionaire")
        
        if "first_dollar" not in unlocked:
            transactions = save.get('transaction_history', [])
            if any(t.get('amount', 0) > 0 and t.get('category') in ["Praca", "Giełda"] for t in transactions):
                self.unlock("first_dollar")

        if "veh_30" in owned_v and "empire_strikes" not in unlocked: self.unlock("empire_strikes")
        if "val_30" in owned_val and "indy_heritage" not in unlocked: self.unlock("indy_heritage")
        
        if len(owned_props) >= 10 and "real_estate_tycoon" not in unlocked: self.unlock("real_estate_tycoon")
        if len(owned_props) >= 3 and "landlord" not in unlocked: self.unlock("landlord")
        if len(owned_props) > 1 and "homeless_no_more" not in unlocked: self.unlock("homeless_no_more")
        
        if save.get('current_job') == "job_20" and "ceo_status" not in unlocked: self.unlock("ceo_status")

        if current_prestige >= 100_000 and "living_legend" not in unlocked: self.unlock("living_legend")
        if current_prestige >= 50_000 and "world_famous" not in unlocked: self.unlock("world_famous")
        if current_prestige >= 10_000 and "social_elite" not in unlocked: self.unlock("social_elite")

    def unlock(self, ach_id):
        """Odblokowuje osiągnięcie i odświeża UI."""
        if ach_id not in self.gv.save_data['unlocked_achievements']:
            self.gv.save_data['unlocked_achievements'].append(ach_id)
            
            if hasattr(self.gv, 'show_achievement_toast'):
                self.gv.show_achievement_toast(ach_id)
            
            if hasattr(self.gv, 'view_home'):
                self.gv.view_home.refresh_view(self.gv.save_data)
            
            print(f"DEBUG: ODBLOKOWANO OSIĄGNIĘCIE: {ach_id}")

    def calculate_portfolio_value(self):
        total = 0
        portfolio = self.gv.save_data.get('portfolio', {})
        market = self.gv.save_data.get('market_data', {})
        for m_type in ['stocks', 'crypto']:
            for sym, data in portfolio.get(m_type, {}).items():
                price = market.get(m_type, {}).get(sym, {}).get('current_price', 0)
                total += data['amount'] * price
        return total

    def calculate_sector_value(self, sector_id):
        total = 0
        portfolio = self.gv.save_data.get('portfolio', {}).get('stocks', {})
        market_stocks = self.gv.save_data.get('market_data', {}).get('stocks', {})
        for sym, data in portfolio.items():
            stock_info = market_stocks.get(sym, {})
            if stock_info.get('category', '').lower() == sector_id.lower():
                total += data['amount'] * stock_info.get('current_price', 0)
        return total

    def calculate_age(self):
        dob_str = self.gv.save_data.get('date_of_birth', '2000-01-01')
        curr_str = self.gv.save_data.get('current_game_date', '2025-01-01')
        try:
            dob = datetime.strptime(dob_str[:10], "%Y-%m-%d")
            curr = datetime.strptime(curr_str[:10], "%Y-%m-%d")
            age = curr.year - dob.year
            if (curr.month, curr.day) < (dob.month, dob.day):
                age -= 1
            return age
        except: return 0