from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class PortfolioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("YOUR ASSETS")
        self.label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2ecc71; margin: 10px 0px;")
        self.layout.addWidget(self.label)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Asset", "Amount", "Avg. Price", "Current Price", "Profit/Loss", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #aaa; padding: 5px; border: none; }
        """)
        self.layout.addWidget(self.table)

    def refresh_view(self, save_data):
        """Method called by GameView when changing tabs."""
        self.save_data = save_data
        portfolio = self.save_data.get('portfolio', {})
        market_data = self.save_data.get('market_data', {})
        
        self.table.setRowCount(0)
        
        for category in ['stocks', 'crypto']:
            assets = portfolio.get(category, {})
            for symbol, p_data in assets.items():
                amount = p_data.get('amount', 0)
                if amount <= 0: continue
                
                m_info = market_data.get(category, {}).get(symbol, {})
                current_price = m_info.get('current_price', 0)
                avg_price = p_data.get('avg_price', 0)
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(f"{symbol}"))
                self.table.setItem(row, 1, QTableWidgetItem(f"{amount:,.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"${avg_price:,.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"${current_price:,.2f}"))
                
                total_value = amount * current_price
                total_cost = amount * avg_price
                profit = total_value - total_cost
                
                profit_item = QTableWidgetItem(f"${profit:+,.2f}")
                profit_item.setForeground(QColor("#2ecc71" if profit >= 0 else "#e74c3c"))
                self.table.setItem(row, 4, profit_item)
                
                sell_btn = QPushButton("SELL")
                sell_btn.setStyleSheet("""
                    QPushButton { background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px; padding: 5px; }
                    QPushButton:hover { background-color: #e74c3c; }
                """)
                sell_btn.clicked.connect(lambda checked, s=symbol, c=category, p=current_price, a=amount: 
                                         self.execute_sell(s, c, p, a))
                self.table.setCellWidget(row, 5, sell_btn)

    def execute_sell(self, symbol, category, current_price, owned_amount):
        """Opens an input dialog to choose amount before selling."""
        from PyQt6.QtWidgets import QInputDialog

        amount_to_sell, ok = QInputDialog.getDouble(
            self, "Sell Asset", 
            f"How much {symbol} do you want to sell? (Max: {owned_amount})",
            value=owned_amount, min=0.01, max=owned_amount, decimals=2
        )

        if not ok or amount_to_sell <= 0:
            return

        main_game = self.parent()
        while main_game is not None:
            if hasattr(main_game, 'save_data'): break
            main_game = main_game.parent()

        if main_game:
            revenue = amount_to_sell * current_price
            
            main_game.log_transaction("Stock Market", f"Sold {amount_to_sell:.2f} {symbol}", revenue)
           
            main_game.save_data['balance'] += revenue
            main_game.save_data['portfolio'][category][symbol]['amount'] -= amount_to_sell
            
            if main_game.save_data['portfolio'][category][symbol]['amount'] < 0.001:
                main_game.save_data['portfolio'][category][symbol]['amount'] = 0

            main_game.update_money_display()
            self.refresh_view(main_game.save_data)
            
            QMessageBox.information(self, "Sale Confirmed", 
                f"Sold {amount_to_sell:.2f} {symbol} for ${revenue:,.2f}")