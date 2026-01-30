import json
import os

class EventManager:
    def __init__(self, events_file="events.json"):
        # Szukamy pliku w głównym katalogu projektu
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.events_path = os.path.join(base_dir, "data", events_file)
        
        print(f"DEBUG: Szukam eventów w: {self.events_path}") # To pomoże Ci sprawdzić ścieżkę
        self.events_db = self.load_events()
        self.active_events = []

    def load_events(self):
        if not os.path.exists(self.events_path):
            print(f"DEBUG: Nie znaleziono pliku {self.events_path}")
            return []
        try:
            with open(self.events_path, "r", encoding="utf-8") as f:
                return json.load(f).get("events", [])
        except Exception as e:
            print(f"DEBUG: Błąd ładowania eventów: {e}")
            return []

    def trigger_event_by_id(self, event_id):
        event = next((e for e in self.events_db if e['id'].upper() == event_id.upper()), None)
        if event:
            if not any(a['event']['id'] == event['id'] for a in self.active_events):
                self.active_events.append({"event": event, "remaining": event['duration']})
                return f"Started: {event['name']}"
            return "Event is already active"
        return f"Unknown Event ID: {event_id}"

    def process_day(self):
        for active in self.active_events[:]:
            active['remaining'] -= 1
            if active['remaining'] <= 0:
                self.active_events.remove(active)

    def get_modifier_for_symbol(self, symbol, sector):
        modifier = 1.0
        for active in self.active_events:
            ev = active['event']
            if ev['target_type'] == "global":
                modifier *= ev['impact']
            elif ev['target_type'] == "sector" and ev['target_id'].lower() == sector.lower():
                modifier *= ev['impact']
            elif ev['target_type'] == "single" and ev['target_id'].upper() == symbol.upper():
                modifier *= ev['impact']
        return modifier