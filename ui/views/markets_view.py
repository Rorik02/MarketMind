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
        self.parent_ctrl = parent # Referencja do głównego kontrolera
        self.save_data = {}
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.stock_tab = QWidget()
        self.crypto_tab = QWidget()
        
        self.tabs.addTab(self.stock_tab, "📈 Stocks")
        self.tabs.addTab(self.crypto_tab, "₿ Crypto")
        
        self.setup_tab_layout(self.stock_tab, "stocks")
        self.setup_tab_layout(self.crypto_tab, "crypto")
        
        self.layout.addWidget(self.tabs)

    def setup_tab_layout(self, tab, market_type):
        layout = QVBoxLayout(tab)
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
                table.setItem(row, 1, QTableWidgetItem(f"${data['current_price']:,}"))
                
                # 3. Zmiana 24h
                history_data = data.get('history', [])
                if history_data:
                    self.set_change_item(table, row, history_data)
                else:
                    table.setItem(row, 2, QTableWidgetItem("N/A"))

                # 4. Dywidenda
                div_rate = data.get('dividend_yield', 0)
                div_item = QTableWidgetItem(f"{div_rate*100:.3f}%" if div_rate > 0 else "0%")
                div_item.setForeground(QColor("#2ecc71" if div_rate > 0 else "#aaaaaa"))
                table.setItem(row, 3, div_item)
                
                # 5. Przycisk Chart - Podgląd wykresu
                chart_btn = QPushButton("View Chart")
                chart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                # Przekazujemy s=symbol i t=m_type, aby lambda nie brała ostatniej wartości z pętli
                chart_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.open_chart(s, t))
                table.setCellWidget(row, 4, chart_btn)
                
                # 6. Przycisk BUY - NAPRAWIONY (Podpięty pod funkcję)
                buy_btn = QPushButton("BUY")
                buy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                buy_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                # PODPIĘCIE: Wywołuje nową metodę buy_asset
                buy_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.buy_asset(s, t))
                table.setCellWidget(row, 5, buy_btn)

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
        """Kupuje 1 sztukę wybranego aktywa bezpośrednio."""
        # 1. Pobieramy dane o cenie z aktualnego widoku
        market_info = self.save_data.get('market_data', {}).get(market_type, {})
        asset_data = market_info.get(symbol)
        
        if not asset_data:
            return

        price = asset_data['current_price']
        
        # 2. Sprawdzamy, czy gracz ma dość pieniędzy
        if self.save_data.get('balance', 0) >= price:
            # Pobieramy środki
            self.save_data['balance'] -= price
            
            # 3. Dodajemy do portfela
            if 'portfolio' not in self.save_data:
                self.save_data['portfolio'] = {'stocks': {}, 'crypto': {}}
            
            portfolio = self.save_data['portfolio'][market_type]
            
            # Zwiększamy ilość o 1
            if symbol in portfolio:
                portfolio[symbol]['amount'] += 1
                # Aktualizujemy średnią cenę zakupu (potrzebne do statystyk)
                portfolio[symbol]['avg_price'] = (portfolio[symbol]['avg_price'] + price) / 2
            else:
                portfolio[symbol] = {
                    'amount': 1,
                    'avg_price': price,
                    'name': asset_data['name']
                }
            
            # 4. Logujemy transakcję i odświeżamy UI
            self.parent_ctrl.log_transaction("Giełda", f"Zakup 1.0 {symbol}", -price)
            self.parent_ctrl.update_money_display()
            
            print(f"Zakupiono {symbol} za ${price}")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Błąd", "Nie masz wystarczającej ilości środków!")

    def open_chart(self, symbol, market_type):
        market_info = self.save_data.get('market_data', {}).get(market_type, {})
        asset_data = market_info.get(symbol)
        
        # Zabezpieczenie: jeśli historia jest pusta, stwórz sztuczny punkt z obecnej ceny
        history = asset_data.get('history', []) if asset_data else []
        
        if asset_data:
            if not history:
                history = [{"date": "Start", "price": asset_data['current_price']}]
            
            chart_win = StockChartWindow(symbol, history, self)
            chart_win.exec()