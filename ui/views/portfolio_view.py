from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class PortfolioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Nagłówek
        self.label = QLabel("TWOJE AKTYWA")
        self.label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2ecc71; margin: 10px 0px;")
        self.layout.addWidget(self.label)

        # Tabela portfela
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Aktywo", "Ilość", "Śr. Cena", "Aktualna", "Zysk/Strata", "Akcja"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #2d2d2d; color: #aaa; padding: 5px; border: none; }
        """)
        self.layout.addWidget(self.table)

    def refresh_view(self, save_data):
        """Metoda wywoływana przez GameView przy zmianie zakładki."""
        self.save_data = save_data
        portfolio = self.save_data.get('portfolio', {})
        market_data = self.save_data.get('market_data', {})
        
        self.table.setRowCount(0)
        
        # Przechodzimy przez kategore: stocks i crypto
        for category in ['stocks', 'crypto']:
            assets = portfolio.get(category, {})
            for symbol, p_data in assets.items():
                amount = p_data.get('amount', 0)
                if amount <= 0: continue # Nie pokazuj sprzedanych/pustych
                
                # Pobierz aktualną cenę z rynku
                m_info = market_data.get(category, {}).get(symbol, {})
                current_price = m_info.get('current_price', 0)
                avg_price = p_data.get('avg_price', 0)
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Wypełnianie danych
                self.table.setItem(row, 0, QTableWidgetItem(f"{symbol}"))
                self.table.setItem(row, 1, QTableWidgetItem(f"{amount:,.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"${avg_price:,.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"${current_price:,.2f}"))
                
                # Obliczanie Zysku/Straty
                total_value = amount * current_price
                total_cost = amount * avg_price
                profit = total_value - total_cost
                
                profit_item = QTableWidgetItem(f"${profit:+,.2f}")
                # Kolorowanie: Zielony jeśli zysk, Czerwony jeśli strata
                profit_item.setForeground(QColor("#2ecc71" if profit >= 0 else "#e74c3c"))
                self.table.setItem(row, 4, profit_item)
                
                # Przycisk Sprzedaży
                sell_btn = QPushButton("SPRZEDAJ")
                sell_btn.setStyleSheet("""
                    QPushButton { background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px; padding: 5px; }
                    QPushButton:hover { background-color: #e74c3c; }
                """)
                # Używamy tej samej logiki szukania main_game co przy zakupie
                sell_btn.clicked.connect(lambda checked, s=symbol, c=category, p=current_price, a=amount: 
                                         self.execute_sell(s, c, p, a))
                self.table.setCellWidget(row, 5, sell_btn)

    def execute_sell(self, symbol, category, current_price, owned_amount):
        """Otwiera okno wyboru ilości przed sprzedażą."""
        from PyQt6.QtWidgets import QInputDialog

        # 1. Okno wyboru ilości
        amount_to_sell, ok = QInputDialog.getDouble(
            self, "Sprzedaż", 
            f"Ile {symbol} chcesz sprzedać? (Max: {owned_amount})",
            value=owned_amount, min=0.01, max=owned_amount, decimals=2
        )

        if not ok or amount_to_sell <= 0:
            return

        # 2. SZUKANIE GAMEVIEW
        main_game = self.parent()
        while main_game is not None:
            if hasattr(main_game, 'save_data'): break
            main_game = main_game.parent()

        if main_game:
            revenue = amount_to_sell * current_price
            
            # --- DODANO LOGOWANIE DO HISTORII ---
            # Rejestrujemy sprzedaż jako przychód (dodatnia kwota)
            main_game.log_transaction("Giełda", f"Sprzedaż {amount_to_sell:.2f} {symbol}", revenue)
            # ------------------------------------

            # Aktualizacja danych
            main_game.save_data['balance'] += revenue
            main_game.save_data['portfolio'][category][symbol]['amount'] -= amount_to_sell
            
            # Jeśli sprzedano wszystko, usuwamy wpis lub zostawiamy 0
            if main_game.save_data['portfolio'][category][symbol]['amount'] < 0.001:
                main_game.save_data['portfolio'][category][symbol]['amount'] = 0

            # Odświeżenie wszystkiego
            main_game.update_money_display()
            self.refresh_view(main_game.save_data)
            
            QMessageBox.information(self, "Sprzedano", 
                f"Sprzedano {amount_to_sell:.2f} {symbol} za ${revenue:,.2f}")