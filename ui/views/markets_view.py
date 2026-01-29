from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.windows.chart_window import StockChartWindow

class MarketsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = {}
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.stock_tab = QWidget()
        self.crypto_tab = QWidget()
        
        self.tabs.addTab(self.stock_tab, "📈 Stocks")
        self.tabs.addTab(self.crypto_tab, "₿ Crypto")
        
        # Zwiększamy liczbę kolumn do 6, aby zmieścić dywidendę
        self.setup_tab_layout(self.stock_tab, "stocks")
        self.setup_tab_layout(self.crypto_tab, "crypto")
        
        self.layout.addWidget(self.tabs)

    def setup_tab_layout(self, tab, market_type):
        layout = QVBoxLayout(tab)
        # Dodajemy kolumnę "Dividend" przed przyciskami
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["Name", "Price", "24h Change", "Dividend", "Trend", "Trade"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #aaa; padding: 5px; border: none; }
        """)
        
        setattr(self, f"{market_type}_table", table)
        layout.addWidget(table)

    def refresh_view(self, save_data):
        self.save_data = save_data
        market_info = self.save_data.get('market_data', {})
        
        for m_type in ["stocks", "crypto"]:
            table = getattr(self, f"{m_type}_table")
            items = market_info.get(m_type, {})
            
            table.setRowCount(len(items))
            for row, (symbol, data) in enumerate(items.items()):
                # 1. Nazwa i Symbol
                table.setItem(row, 0, QTableWidgetItem(f"{data['name']} ({symbol})"))
                
                # 2. Cena
                price_item = QTableWidgetItem(f"${data['current_price']:,}")
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 1, price_item)
                
                # 3. Zmiana 24h
                self.set_change_item(table, row, data['history'])

                # 4. --- NOWOŚĆ: WYŚWIETLANIE DYWIDENDY ---
                div_rate = data.get('dividend_yield', 0)
                if div_rate > 0:
                    # Wyświetlamy jako procent miesięczny (np. 0.058%)
                    div_text = f"{div_rate*100:.3f}% / msc"
                    div_color = QColor("#2ecc71") # Zielony dla płacących
                else:
                    div_text = "0%"
                    div_color = QColor("#aaaaaa") # Szary dla braku dywidendy

                div_item = QTableWidgetItem(div_text)
                div_item.setForeground(div_color)
                div_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 3, div_item)
                
                # 5. PRZYCISK WYKRESU (kolumna 4)
                chart_btn = QPushButton("View Chart")
                chart_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.open_chart(s, t))
                table.setCellWidget(row, 4, chart_btn)
                
                # 6. PRZYCISK KUPNA (kolumna 5)
                buy_btn = QPushButton("BUY")
                buy_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                buy_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.open_chart(s, t))
                table.setCellWidget(row, 5, buy_btn)

    def set_change_item(self, table, row, history):
        if len(history) < 2: return
        change = ((history[-1]['price'] - history[-2]['price']) / history[-2]['price']) * 100
        item = QTableWidgetItem(f"{change:+.2f}%")
        item.setForeground(QColor("#2ecc71" if change >= 0 else "#e74c3c"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 2, item)

    def open_chart(self, symbol, market_type):
        market_info = self.save_data.get('market_data', {}).get(market_type, {})
        asset_data = market_info.get(symbol)
        
        if asset_data and 'history' in asset_data:
            chart_win = StockChartWindow(symbol, asset_data['history'], self)
            chart_win.exec()