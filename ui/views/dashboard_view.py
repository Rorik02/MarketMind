import pyqtgraph as pg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGraphicsPathItem, QGraphicsEllipseItem, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QColor, QPainterPath
from PyQt6.QtCore import Qt
import os
import json

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #121212; color: white;")

        # --- GÓRA: TYTUŁ ---
        header = QLabel("DASHBOARD FINANSOWY")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #3a96dd; margin-bottom: 10px;")
        self.layout.addWidget(header)

        # --- ŚRODEK: STATYSTYKI + WYKRES ---
        self.top_content = QHBoxLayout()
        
        self.stats_layout = QVBoxLayout()
        self.stat_widgets = {}
        self.categories_config = [
            ("Gotówka", "#2ecc71"),
            ("Akcje i Krypto", "#3a96dd"),
            ("Pojazdy", "#f1c40f"),
            ("Nieruchomości", "#9b59b6"),
            ("Drogocenności", "#e67e22") 
        ]
        
        for name, color in self.categories_config:
            frame = QFrame()
            frame.setStyleSheet(f"background: #1e1e1e; border-left: 5px solid {color}; border-radius: 5px;")
            f_layout = QVBoxLayout(frame)
            lbl_display = QLabel(f"{name}: [$0.00]")
            lbl_display.setStyleSheet("font-size: 14px; font-weight: bold;")
            f_layout.addWidget(lbl_display)
            self.stat_widgets[name] = lbl_display
            self.stats_layout.addWidget(frame)
        
        self.top_content.addLayout(self.stats_layout, 1)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#121212')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.hideAxis('left')
        self.top_content.addWidget(self.plot_widget, 1)
        self.layout.addLayout(self.top_content)

        # --- PODSUMOWANIE NET WORTH ---
        self.total_net_worth = QLabel("NET WORTH: $0.00")
        self.total_net_worth.setStyleSheet("font-size: 24px; font-weight: bold; color: #2ecc71; margin: 10px 0;")
        self.total_net_worth.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.total_net_worth)

        # --- DÓŁ: HISTORIA TRANSAKCJI ---


    def calculate_val(self, save_data, json_file, save_key):
        owned_ids = save_data.get(save_key, [])
        total = 0
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", json_file)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for i in items:
                    if i['id'] in owned_ids:
                        total += i.get('price', 0)
        return total

    def refresh_view(self, save_data):
        # 1. Obliczenia
        cash = save_data.get('balance', 0)
        market_val = 0
        portfolio = save_data.get('portfolio', {})
        market_data = save_data.get('market_data', {})
        for cat in ['stocks', 'crypto']:
            for sym, p_data in portfolio.get(cat, {}).items():
                price = market_data.get(cat, {}).get(sym, {}).get('current_price', 0)
                market_val += p_data.get('amount', 0) * price
        
        vehicles_val = self.calculate_val(save_data, "vehicles.json", "owned_vehicles")
        houses_val = self.calculate_val(save_data, "properties.json", "owned_properties")
        valuables_val = self.calculate_val(save_data, "valuables.json", "owned_valuables")
        
        total = cash + market_val + vehicles_val + houses_val + valuables_val
        vals = {"Gotówka": cash, "Akcje i Krypto": market_val, "Pojazdy": vehicles_val, "Nieruchomości": houses_val, "Drogocenności": valuables_val}
        
        for name, val in vals.items():
            self.stat_widgets[name].setText(f"{name}: [${val:,.2f}]")
        self.total_net_worth.setText(f"NET WORTH: ${total:,.2f}")

        # 2. Wykres
        self.plot_widget.clear()
        if total > 0:
            current_angle = 0
            rect = pg.QtCore.QRectF(-10, -10, 20, 20) 
            for name, color in self.categories_config:
                val = vals[name]
                if val <= 0: continue
                span_angle = (val / total) * 360
                path = QPainterPath()
                path.moveTo(0, 0)
                path.arcTo(rect, current_angle, span_angle)
                path.lineTo(0, 0)
                item = pg.QtWidgets.QGraphicsPathItem(path)
                item.setBrush(pg.mkBrush(color))
                item.setPen(pg.mkPen('#121212', width=1))
                self.plot_widget.addItem(item)
                current_angle += span_angle

            hole = pg.QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
            hole.setBrush(pg.mkBrush('#121212'))
            self.plot_widget.addItem(hole)
            self.plot_widget.setRange(xRange=[-12, 12], yRange=[-12, 12])