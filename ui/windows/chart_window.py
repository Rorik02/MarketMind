import pyqtgraph as pg
import math
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class StockChartWindow(QDialog):
    def __init__(self, symbol, history_data, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.history_data = history_data
        
        if not history_data:
            self.current_price = 0
        else:
            self.current_price = history_data[-1]['price']
        
        self.setWindowTitle(f"Market Chart - {symbol}")
        self.setMinimumSize(1000, 600)
        
        self.main_layout = QHBoxLayout(self)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.left_container = QVBoxLayout()
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.info_label = QLabel("Hover over the chart to see price details")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3a96dd;")
        
        self.left_container.addWidget(self.plot_widget)
        self.left_container.addWidget(self.info_label)
        self.main_layout.addLayout(self.left_container, 3) 

        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(15)
        self.right_panel.setContentsMargins(10, 0, 0, 0)
        
        title_text = f"TRADE {symbol}"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2ecc71;")
        self.right_panel.addWidget(title)

        self.price_display = QLabel(f"Current Price: ${self.current_price:,.2f}")
        self.price_display.setStyleSheet("font-size: 15px; color: #aaaaaa;")
        self.right_panel.addWidget(self.price_display)

        input_container = QHBoxLayout()
        input_container.setSpacing(0)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter quantity...")
        self.amount_input.setStyleSheet("""
            background: #2a2a2a; color: white; padding: 10px; 
            border: 1px solid #444; border-top-left-radius: 5px; 
            border-bottom-left-radius: 5px; font-size: 14px;
        """)
        self.amount_input.textChanged.connect(self.update_total_cost)
        
        self.btn_max = QPushButton("MAX")
        self.btn_max.setFixedSize(60, 39)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.setStyleSheet("""
            QPushButton { 
                background-color: #f39c12; color: white; font-weight: bold; 
                border-top-right-radius: 5px; border-bottom-right-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.btn_max.clicked.connect(self.calculate_max_amount)
        
        input_container.addWidget(self.amount_input)
        input_container.addWidget(self.btn_max)
        self.right_panel.addLayout(input_container)

        self.total_cost_lbl = QLabel("Total Cost: $0.00")
        self.total_cost_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.right_panel.addWidget(self.total_cost_lbl)

        self.buy_btn = QPushButton("CONFIRM PURCHASE")
        self.buy_btn.setFixedHeight(50)
        self.buy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.buy_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; border-radius: 8px; font-size: 14px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.buy_btn.clicked.connect(self.execute_trade)
        self.right_panel.addWidget(self.buy_btn)
        
        self.right_panel.addStretch() 
        self.main_layout.addLayout(self.right_panel, 1)

        if history_data:
            self.setup_chart_data()

    def calculate_max_amount(self):
        main_game = self.find_main_game()
        if main_game and self.current_price > 0:
            balance = main_game.save_data.get('balance', 0)
            max_qty = math.floor(balance / self.current_price)
            self.amount_input.setText(str(max_qty))

    def find_main_game(self):
        curr = self.parent()
        while curr is not None:
            if hasattr(curr, 'save_data') and hasattr(curr, 'log_transaction'):
                return curr
            curr = curr.parent()
        return None

    def setup_chart_data(self):
        self.dates = [i for i in range(len(self.history_data))]
        self.prices = [point['price'] for point in self.history_data]
        self.raw_dates = [point['date'] for point in self.history_data]

        ticks = []
        num_ticks = 6
        if len(self.raw_dates) > 0:
            step = max(1, len(self.raw_dates) // num_ticks)
            for i in range(0, len(self.raw_dates), step):
                full_date = self.raw_dates[i] 
                short_date = "-".join(full_date.split("-")[1:]) 
                ticks.append((i, short_date))
                
        ax = self.plot_widget.getAxis('bottom')
        ax.setTicks([ticks])

        pen = pg.mkPen(color='#3a96dd', width=3)
        self.plot_widget.plot(self.dates, self.prices, pen=pen)
        self.plot_widget.plot(self.dates, self.prices, pen=None, symbol='o', symbolSize=5, symbolBrush='#3a96dd')

        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen='#ffffff55')
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen='#ffffff55')
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def update_total_cost(self):
        try:
            text = self.amount_input.text().replace(',', '.')
            amount = float(text) if text else 0
            total = amount * self.current_price
            self.total_cost_lbl.setText(f"Total Cost: ${total:,.2f}")
        except ValueError:
            self.total_cost_lbl.setText("Total Cost: $0.00")

    def mouseMoved(self, evt):
        pos = evt[0]
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if 0 <= index < len(self.prices):
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())
                self.info_label.setText(f"📅 Date: {self.raw_dates[index]} | 💰 Price: ${self.prices[index]:,.2f}")

    def execute_trade(self):
        try:
            main_game = self.find_main_game()
            if not main_game: return

            amount_text = self.amount_input.text().strip().replace(',', '.')
            if not amount_text: return
            amount = float(amount_text)
            if amount <= 0: return

            total_cost = amount * self.current_price
            
            if main_game.save_data['balance'] < total_cost:
                QMessageBox.warning(self, "Brak środków", "Nie stać Cię na ten zakup!")
                return

            market_data = main_game.save_data.get('market_data', {})
            p_key = "stocks" if self.symbol in market_data.get('stocks', {}) else "crypto"
            asset_info = market_data[p_key][self.symbol]
            
            if 'portfolio' not in main_game.save_data:
                main_game.save_data['portfolio'] = {"stocks": {}, "crypto": {}}
            
            portfolio = main_game.save_data['portfolio'].setdefault(p_key, {})
            p_item = portfolio.setdefault(self.symbol, {"amount": 0, "avg_price": 0, "name": asset_info['name']})
            
            current_total_value = p_item["amount"] * p_item["avg_price"]
            new_amount = p_item["amount"] + amount
            new_avg = (current_total_value + total_cost) / new_amount
            
            p_item["amount"] = new_amount
            p_item["avg_price"] = round(new_avg, 2)
            
            main_game.save_data['balance'] -= total_cost
            
            main_game.log_transaction("Giełda", f"Zakup {amount} {self.symbol}", -total_cost)
            main_game.update_money_display() 
            
            if hasattr(main_game, 'view_home'):
                main_game.view_home.refresh_view(main_game.save_data)
            if hasattr(main_game, 'view_markets'):
                main_game.view_markets.refresh_view(main_game.save_data)

            QMessageBox.information(self, "Sukces", f"Kupiono {amount} jednostek {self.symbol}!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Transakcja nieudana: {str(e)}")