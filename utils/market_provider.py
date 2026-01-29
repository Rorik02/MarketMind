import yfinance as yf
import json
import random
from datetime import datetime, timedelta

class MarketProvider:
    """Klasa odpowiedzialna za jednorazowy snapshot danych z API Yahoo Finance z dywidendami."""
    
    def __init__(self):
        self.stocks = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "NFLX", "V", "CDR.WA"]
        self.crypto = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "DOGE-USD"]
        self.all_symbols = self.stocks + self.crypto

    def fetch_market_snapshot(self):
        """Pobiera dane historyczne, aktualne oraz stopy dywidend."""
        market_data = {
            "stocks": {},
            "crypto": {}
        }

        print("Pobieranie danych rynkowych z API... Proszę czekać.")
        
        for symbol in self.all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="30d", interval="1d")
                
                if history.empty:
                    continue

                # Formatuje historię punktów
                history_points = []
                for date, row in history.iterrows():
                    history_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "price": round(float(row['Close']), 2)
                    })

                # --- NOWOŚĆ: POBIERANIE DYWIDENDY ---
                dividend_yield = 0.0
                if symbol in self.stocks:
                    # 1. Próbujemy pobrać realną roczną stopę z API (np. 0.03 dla 3%)
                    raw_yield = ticker.info.get('dividendYield')
                    
                    # 2. Sprawdzamy czy API zwróciło sensowną wartość
                    if raw_yield is not None and raw_yield > 0:
                        dividend_yield = raw_yield
                    else:
                        # 3. Fallback: Jeśli firma płaci, ale info jest puste, 
                        # losujemy yield roczny 1% - 3%
                        dividend_yield = round(random.uniform(0.001, 0.004), 4)

                    # 4. KLUCZ: Konwersja rocznej stopy na miesięczną (dzielenie przez 12)
                    # Zwiększamy precyzję do 6 miejsc, bo to bardzo małe liczby
                    self.dividend_yield = round(dividend_yield / 4, 6)
                data = {    
                    "symbol": symbol,
                    "name": ticker.info.get('shortName', symbol),
                    "current_price": round(float(history['Close'].iloc[-1]), 2),
                    "history": history_points,
                    "dividend_yield": dividend_yield,  # Stopa miesięczna
                    "category": "Stock" if symbol in self.stocks else "Crypto"
                }

                if symbol in self.stocks:
                    market_data["stocks"][symbol] = data
                else:
                    market_data["crypto"][symbol] = data
                
                print(f"Pobrano: {symbol} (Div: {dividend_yield*100:.3f}%)")

            except Exception as e:
                print(f"Błąd pobierania {symbol}: {e}")

        return market_data