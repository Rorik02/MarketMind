import yfinance as yf
import json
from datetime import datetime, timedelta

class MarketProvider:
    """Klasa odpowiedzialna za jednorazowy snapshot danych z API Yahoo Finance."""
    
    def __init__(self):
        self.stocks = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "NFLX", "V", "CDR.WA"]
        self.crypto = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "DOGE-USD"]
        self.all_symbols = self.stocks + self.crypto

    def fetch_market_snapshot(self):
        """Pobiera dane historyczne i aktualne dla wszystkich zdefiniowanych symboli."""
        market_data = {
            "stocks": {},
            "crypto": {}
        }

        print("Pobieranie danych z API... Proszę czekać.")
        
        for symbol in self.all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                # Pobieramy historię z ostatnich 30 dni (interwał 1-dniowy)
                history = ticker.history(period="30d", interval="1d")
                
                if history.empty:
                    continue

                # Formatuje historię do listy punktów dla wykresu
                history_points = []
                for date, row in history.iterrows():
                    history_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "price": round(float(row['Close']), 2)
                    })

                data = {
                    "symbol": symbol,
                    "name": ticker.info.get('shortName', symbol),
                    "current_price": round(float(history['Close'].iloc[-1]), 2),
                    "history": history_points,
                    "category": "Stock" if symbol in self.stocks else "Crypto"
                }

                if symbol in self.stocks:
                    market_data["stocks"][symbol] = data
                else:
                    market_data["crypto"][symbol] = data
                
                print(f"Pobrano: {symbol}")

            except Exception as e:
                print(f"Błąd pobierania {symbol}: {e}")

        return market_data