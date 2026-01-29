from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class HistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_data = []
        self.current_page = 0
        self.page_size = 50 # Ile transakcji na jednej stronie
        
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #121212; color: white;")

        # Header
        header = QLabel("📜 PEŁNA HISTORIA FINANSOWA")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #f1c40f;")
        self.layout.addWidget(header)

        # Tabela
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Data", "Kategoria", "Opis", "Kwota"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #1a1a1a; color: #eee; }")
        self.layout.addWidget(self.table)

        # Nawigacja stronami
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅ Poprzednia strona")
        self.next_btn = QPushButton("Następna strona ➡")
        self.page_lbl = QLabel("Strona: 1 / 1")
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setFixedSize(150, 30)
            btn.setStyleSheet("background: #333; color: white; border-radius: 5px;")
            nav_layout.addWidget(btn)
        
        nav_layout.insertWidget(1, self.page_lbl)
        self.layout.addLayout(nav_layout)

        # Logika przycisków
        self.prev_btn.clicked.connect(lambda: self.change_page(-1))
        self.next_btn.clicked.connect(lambda: self.change_page(1))

    def refresh_view(self, save_data):
        self.history_data = save_data.get('transaction_history', [])
        self.update_table()

    def update_table(self):
        total_pages = max(1, (len(self.history_data) + self.page_size - 1) // self.page_size)
        
        # Zabezpieczenie zakresu stron
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        if self.current_page < 0: self.current_page = 0

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_items = self.history_data[start_idx:end_idx]

        self.table.setRowCount(len(page_items))
        for row, entry in enumerate(page_items):
            self.table.setItem(row, 0, QTableWidgetItem(entry['date']))
            self.table.setItem(row, 1, QTableWidgetItem(entry['category']))
            self.table.setItem(row, 2, QTableWidgetItem(entry['description']))
            
            amt = entry['amount']
            amt_item = QTableWidgetItem(f"{amt:+,.2f}$")
            amt_item.setForeground(QColor("#2ecc71" if amt > 0 else "#e74c3c"))
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 3, amt_item)

        self.page_lbl.setText(f"Strona: {self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

    def change_page(self, delta):
        self.current_page += delta
        self.update_table()