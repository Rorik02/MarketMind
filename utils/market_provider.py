import yfinance as yf
import json
import random
import os

class MarketProvider:
    def __init__(self):
        # 100+ Symboli podzielonych na sektory
        tech = ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "META", "TSLA", "INTC", "ASML", "ORCL", "CRM", "ADBE", "CSCO", "IBM", "TXN", "QCOM", "AMAT", "MU", "SNPS", "PLTR"]
        defense = ["LMT", "BA", "RTX", "NOC", "GD", "LHX", "BWXT", "AIR.PA", "RHM.DE", "PLD.WA", "HWM", "TDG", "TXT", "LDOS", "HEI"]
        finance = ["JPM", "GS", "V", "MA", "HSBC", "BAC", "MS", "AXP", "PYPL", "PKO.WA", "PEO.WA", "ING.WA", "DBK.DE", "BNP.PA", "BLK"]
        energy = ["XOM", "SHEL", "RIO", "BP", "CVX", "TTE.PA", "COP", "SLB", "EOG", "KGH.WA", "PGE.WA", "PKN.WA", "VALE", "FCX", "NEM"]
        retail = ["AMZN", "WMT", "COST", "PG", "KO", "PEP", "NKE", "EL", "LVMH.PA", "OR.PA", "ALE.WA", "DIN.WA", "MCD", "SBUX", "TGT"]
        health = ["PFE", "JNJ", "UNH", "LLY", "ABBV", "MRK", "AZN", "NVS", "MRNA", "TMO"]
        industry = ["F", "GM", "VOW3.DE", "BMW.DE", "PAH3.DE", "CAT", "DE", "MMM", "GE", "HON"]
        crypto = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "DOGE-USD", "XRP-USD", "ADA-USD", "DOT-USD", "LINK-USD", "MATIC-USD"]

        self.stocks = tech + defense + finance + energy + retail + health + industry
        self.crypto = crypto
        self.all_symbols = self.stocks + self.crypto
        self.cache_file = "market_data_snapshot.json"

    def get_market_data(self):
        """Ładuje dane z pliku lub pobiera nowe, jeśli pliku brak."""
        if os.path.exists(self.cache_file):
            print("--- Wczytywanie giełdy z cache (Szybki start) ---")
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return self.fetch_market_snapshot()

    def fetch_market_snapshot(self):
        market_data = {"stocks": {}, "crypto": {}}
        print(f"Pobieranie {len(self.all_symbols)} firm. Cierpliwości...")

        for i, symbol in enumerate(self.all_symbols):
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="7d")
                if history.empty: continue

                # Historia dla wykresów w UI
                history_points = [{"date": d.strftime("%Y-%m-%d"), "price": round(float(r['Close']), 2)} 
                                 for d, r in history.iterrows()]

                current_price = round(float(history['Close'].iloc[-1]), 2)
                
                # Poprawiona logika dywidendy
                raw_yield = ticker.info.get('dividendYield')
                if isinstance(raw_yield, (int, float)) and raw_yield > 0:
                    annual_yield = raw_yield
                else:
                    # Realistyczny fallback: 0.5% - 3.5% rocznie
                    annual_yield = round(random.uniform(0.005, 0.035), 4)

                data = {
                    "symbol": symbol,
                    "name": ticker.info.get('shortName', symbol),
                    "current_price": current_price,
                    "history": history_points,
                    "dividend_yield": round(annual_yield / 4, 6), # Stopa kwartalna
                    "category": "Stock" if symbol in self.stocks else "Crypto"
                }

                target = "stocks" if symbol in self.stocks else "crypto"
                market_data[target][symbol] = data
                
                if (i + 1) % 10 == 0: print(f"Postęp: {i+1}/{len(self.all_symbols)}")
            except Exception as e:
                print(f"Błąd {symbol}: {e}")

        with open(self.cache_file, "w") as f:
            json.dump(market_data, f, indent=4)
        return market_data