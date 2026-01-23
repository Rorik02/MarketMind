from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class MarketsView(QWidget):
    """Widok giełdy i kryptowalut wczytujący dane z save_data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = {}
        self.layout = QVBoxLayout(self)
        
        # Tworzymy zakładki: Akcje i Kryptowaluty
        self.tabs = QTabWidget()
        self.stock_tab = QWidget()
        self.crypto_tab = QWidget()
        
        self.tabs.addTab(self.stock_tab, "📈 Stocks")
        self.tabs.addTab(self.crypto_tab, "₿ Crypto")
        
        self.setup_tab_layout(self.stock_tab, "stocks")
        self.setup_tab_layout(self.crypto_tab, "crypto")
        
        self.layout.addWidget(self.tabs)

    def setup_tab_layout(self, tab, market_type):
        """Tworzy tabelę dla konkretnego typu rynku."""
        layout = QVBoxLayout(tab)
        
        table = QTableWidget(0, 5) # 5 kolumn: Nazwa, Cena, Zmiana, Wykres, Akcja
        table.setHorizontalHeaderLabels(["Name", "Price", "24h Change", "Trend", "Trade"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Stylizacja tabeli (ciemny motyw pasujący do Twoich screenów)
        table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #aaa; padding: 5px; border: none; }
        """)
        
        setattr(self, f"{market_type}_table", table)
        layout.addWidget(table)

    def refresh_view(self, save_data):
        """Wczytuje świeże dane z save_data do tabel."""
        self.save_data = save_data
        market_data = self.save_data.get('market_data', {})
        
        for m_type in ["stocks", "crypto"]:
            table = getattr(self, f"{m_type}_table")
            items = market_data.get(m_type, {})
            
            table.setRowCount(len(items))
            for row, (symbol, data) in enumerate(items.items()):
                # Kolumna 1: Nazwa i Symbol
                table.setItem(row, 0, QTableWidgetItem(f"{data['name']} ({symbol})"))
                
                # Kolumna 2: Aktualna Cena
                price_item = QTableWidgetItem(f"${data['current_price']:,}")
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 1, price_item)
                
                # Kolumna 3: Zmiana (obliczana z historii)
                self.set_change_item(table, row, data['history'])
                
                # Kolumna 4: Przycisk Wykresu
                chart_btn = QPushButton("View Chart")
                chart_btn.clicked.connect(lambda ch, s=symbol, t=m_type: self.open_chart(s, t))
                table.setCellWidget(row, 3, chart_btn)
                
                # Kolumna 5: Przyciski Kup/Sprzedaj
                trade_layout = QHBoxLayout()
                buy_btn = QPushButton("Buy")
                buy_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                trade_layout.addWidget(buy_btn)
                
                container = QWidget()
                container.setLayout(trade_layout)
                table.setCellWidget(row, 4, container)

    def set_change_item(self, table, row, history):
        """Oblicza zmianę procentową na podstawie historii."""
        if len(history) < 2: return
        last_price = history[-1]['price']
        prev_price = history[-2]['price']
        change = ((last_price - prev_price) / prev_price) * 100
        
        item = QTableWidgetItem(f"{change:+.2f}%")
        item.setForeground(QColor("#2ecc71" if change >= 0 else "#e74c3c"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 2, item)

    def open_chart(self, symbol, market_type):
        """Tutaj wywołamy okno z PyQtGraph, które zaraz stworzymy."""
        print(f"Opening chart for {symbol}")