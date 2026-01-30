import sys
import os

# 1. NAPRAWA PROBLEMU Z MODUŁEM 'ui' (PYTHONPATH)
# Ten blok sprawia, że import 'from ui.windows...' zadziała zawsze
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. POPRAWIONE IMPORTY PYQT6 (DODANO QFrame)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QPushButton, 
    QLabel, QLineEdit, QComboBox, QFrame  # <--- TUTAJ DODANO QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# 3. IMPORT OKNA WYKRESU
try:
    from ui.windows.chart_window import StockChartWindow
except ImportError:
    from windows.chart_window import StockChartWindow


class MarketsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ctrl = parent 
        self.save_data = {}
        self.layout = QVBoxLayout(self)
        
        # --- NOWY PANEL WYSZUKIWANIA I FILTROWANIA ---
        self.filter_panel = QFrame()
        self.filter_panel.setStyleSheet("background-color: #252525; border-radius: 10px;")
        filter_layout = QHBoxLayout(self.filter_panel)
        
        # Wyszukiwarka
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search company or symbol...")
        self.search_input.setStyleSheet("""
            QLineEdit { 
                background-color: #1e1e1e; color: white; padding: 8px; 
                border: 1px solid #444; border-radius: 5px; 
            }
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Filtr Sektorów
        self.sector_filter = QComboBox()
        self.sector_filter.addItems(["All Sectors", "Tech", "Defense", "Energy", "Finance", "Health", "Retail", "Crypto"])
        self.sector_filter.setStyleSheet("""
            QComboBox { 
                background-color: #1e1e1e; color: white; padding: 8px; 
                border: 1px solid #444; min-width: 150px; 
            }
            QAbstractItemView { background-color: #1e1e1e; color: white; selection-background-color: #3a96dd; }
        """)
        self.sector_filter.currentTextChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(QLabel("Sector:"))
        filter_layout.addWidget(self.sector_filter, 1)
        
        self.layout.addWidget(self.filter_panel)
        # --------------------------------------------

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #2d2d2d; color: #aaa; padding: 10px 20px; }
            QTabBar::tab:selected { background: #1e1e1e; color: white; border-bottom: 2px solid #3a96dd; }
        """)
        
        self.stock_tab = QWidget()
        self.crypto_tab = QWidget()
        
        self.tabs.addTab(self.stock_tab, "📈 Stocks")
        self.tabs.addTab(self.crypto_tab, "₿ Crypto")
        
        self.setup_tab_layout(self.stock_tab, "stocks")
        self.setup_tab_layout(self.crypto_tab, "crypto")
        
        self.layout.addWidget(self.tabs)

    def setup_tab_layout(self, tab, market_type):
        layout = QVBoxLayout(tab)
        # Zwiększamy liczbę kolumn do 7, aby dodać ukrytą kolumnę Sektora do filtrowania
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels(["Name", "Price", "24h Change", "Dividend", "Category", "Trend", "Trade"])
        
        # Ukrywamy kolumnę kategorii (indeks 4), używamy jej tylko do filtrowania logicznego
        table.setColumnHidden(4, True)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #aaa; padding: 5px; border: none; }
        """)
        
        setattr(self, f"{market_type}_table", table)
        layout.addWidget(table)

    def apply_filters(self):
        """Logika filtrowania wierszy z zabezpieczeniem przed błędami danych."""
        search_txt = self.search_input.text().strip().lower()
        sector_txt = self.sector_filter.currentText()
        
        for m_type in ["stocks", "crypto"]:
            table = getattr(self, f"{m_type}_table")
            for row in range(table.rowCount()):
                # Pobieramy nazwę/symbol
                name_item = table.item(row, 0)
                # Pobieramy kategorię z ukrytej kolumny (indeks 4)
                category_item = table.item(row, 4)
                
                if not name_item or not category_item:
                    continue
                    
                name_symbol = name_item.text().lower()
                category = category_item.text()
                
                # Sprawdzanie warunków
                match_search = search_txt in name_symbol
                # Porównanie bez względu na spacje po bokach
                match_sector = (sector_txt == "All Sectors" or category.strip() == sector_txt.strip())
                
                # Pokaż wiersz tylko jeśli oba warunki są spełnione
                table.setRowHidden(row, not (match_search and match_sector))

    def refresh_view(self, save_data):
        self.save_data = save_data
        market_info = self.save_data.get('market_data', {})
        
        # 1. TWOJA MAPA SEKTORÓW (Musisz jej użyć w pętli poniżej)
        sector_map = {
            "AAPL": "Tech", "MSFT": "Tech", "NVDA": "Tech", "AMD": "Tech", "GOOGL": "Tech",
            "META": "Tech", "TSLA": "Tech", "INTC": "Tech", "ASML": "Tech", "ORCL": "Tech",
            "CRM": "Tech", "ADBE": "Tech", "CSCO": "Tech", "IBM": "Tech", "TXN": "Tech", "AMAT": "Tech",
            "LMT": "Defense", "RTX": "Defense", "NOC": "Defense", "GD": "Defense", 
            "LHX": "Defense", "BWXT": "Defense", "AIR.PA": "Defense", "RHM.DE": "Defense",
            "JPM": "Finance", "GS": "Finance", "V": "Finance", "MA": "Finance", "BAC": "Finance",
            "PKO.WA": "Finance", "PEO.WA": "Finance", "ING.WA": "Finance",
            "XOM": "Energy", "CVX": "Energy", "SHEL": "Energy", "BP": "Energy", "COP": "Energy", "PKN.WA": "Energy",
            "PFE": "Health", "JNJ": "Health", "UNH": "Health", "LLY": "Health", "ABBV": "Health",
            "AMZN": "Retail", "WMT": "Retail", "COST": "Retail", "ALE.WA": "Retail"
        }
        
        for m_type in ["stocks", "crypto"]:
            table = getattr(self, f"{m_type}_table")
            items = market_info.get(m_type, {})
            
            table.setRowCount(len(items))
            for row, (symbol, data) in enumerate(items.items()):
                # Kolumny 0-3 (Bez zmian)
                table.setItem(row, 0, QTableWidgetItem(f"{data['name']} ({symbol})"))
                table.setItem(row, 1, QTableWidgetItem(f"${data['current_price']:,}"))
                
                history_data = data.get('history', [])
                if history_data:
                    self.set_change_item(table, row, history_data)
                else:
                    table.setItem(row, 2, QTableWidgetItem("N/A"))

                div_rate = data.get('dividend_yield', 0)
                div_item = QTableWidgetItem(f"{div_rate*100:.3f}%" if div_rate > 0 else "0%")
                div_item.setForeground(QColor("#2ecc71" if div_rate > 0 else "#aaaaaa"))
                table.setItem(row, 3, div_item)

                # --- KLUCZOWA POPRAWKA ---
                # 4. KATEGORIA (Pobieramy z mapy powyżej, a nie z 'data.get')
                if m_type == "crypto":
                    cat_name = "Crypto"
                else:
                    cat_name = sector_map.get(symbol, "Other") # Tutaj używamy Twojej mapy!
                
                table.setItem(row, 4, QTableWidgetItem(cat_name))
                
                # Kolumny 5-6 (Bez zmian)
                chart_btn = QPushButton("View Chart")
                chart_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.open_chart(s, t))
                table.setCellWidget(row, 5, chart_btn)
                
                buy_btn = QPushButton("BUY")
                buy_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 4px;")
                buy_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.buy_asset(s, t))
                table.setCellWidget(row, 6, buy_btn)

        # Na koniec wymuszamy filtrację
        self.apply_filters()

    def set_change_item(self, table, row, history):
        if not history or len(history) < 2: 
            table.setItem(row, 2, QTableWidgetItem("0.00%"))
            return
            
        change = ((history[-1]['price'] - history[-2]['price']) / history[-2]['price']) * 100
        item = QTableWidgetItem(f"{change:+.2f}%")
        item.setForeground(QColor("#2ecc71" if change >= 0 else "#e74c3c"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 2, item)

    def buy_asset(self, symbol, market_type):
        market_info = self.save_data.get('market_data', {}).get(market_type, {})
        asset_data = market_info.get(symbol)
        if not asset_data: return

        price = asset_data['current_price']
        if self.save_data.get('balance', 0) >= price:
            self.save_data['balance'] -= price
            if 'portfolio' not in self.save_data:
                self.save_data['portfolio'] = {'stocks': {}, 'crypto': {}}
            
            portfolio = self.save_data['portfolio'][market_type]
            if symbol in portfolio:
                portfolio[symbol]['amount'] += 1
                portfolio[symbol]['avg_price'] = (portfolio[symbol]['avg_price'] + price) / 2
            else:
                portfolio[symbol] = {'amount': 1, 'avg_price': price, 'name': asset_data['name']}
            
            self.parent_ctrl.log_transaction("Giełda", f"Zakup 1.0 {symbol}", -price)
            self.parent_ctrl.update_money_display()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Błąd", "Nie masz wystarczającej ilości środków!")

    def open_chart(self, symbol, market_type):
        market_info = self.save_data.get('market_data', {}).get(market_type, {})
        asset_data = market_info.get(symbol)
        if asset_data:
            history = asset_data.get('history', [])
            if not history:
                history = [{"date": "Start", "price": asset_data['current_price']}]
            chart_win = StockChartWindow(symbol, history, self)
            chart_win.exec()