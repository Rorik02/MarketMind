from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QProgressBar, QScrollArea, QMessageBox, QSlider)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BankView(QWidget):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent_ctrl = parent
        self.save_data = save_data or {}
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        header = QLabel("🏦 CENTRAL BANK & LOANS")
        header.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 10px;")
        self.main_layout.addWidget(header)

        loan_title = QLabel("Available Loan Offers")
        loan_title.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        self.main_layout.addWidget(loan_title)

        self.offers_container = QWidget()
        self.offers_layout = QHBoxLayout(self.offers_container)
        self.main_layout.addWidget(self.offers_container)

        active_title = QLabel("Your Active Loans")
        active_title.setStyleSheet("color: #aaaaaa; font-weight: bold; margin-top: 20px;")
        self.main_layout.addWidget(active_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.loans_container = QWidget()
        self.loans_layout = QVBoxLayout(self.loans_container)
        self.loans_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.loans_container)
        self.main_layout.addWidget(self.scroll)

    def create_loan_offer_card(self, offer):
        active_loans = self.save_data.get('active_loans', [])
        num_active = len(active_loans)
        
        penalty_multiplier = 1.0 + (num_active * 0.75)
        adjusted_interest = offer['interest'] * penalty_multiplier
        
        base_total = offer['amount'] * (1 + offer['interest'])
        actual_total = offer['amount'] * (1 + adjusted_interest)
        penalty_cost = actual_total - base_total
        monthly = actual_total / offer['months']
        
        card = QFrame()
        border_color = offer['color'] if num_active == 0 else "#e67e22" 
        card.setStyleSheet(f"background: #252525; border: 2px solid {border_color}; border-radius: 12px; padding: 15px;")
        lay = QVBoxLayout(card)
        
        amt_lbl = QLabel(f"${offer['amount']:,}")
        amt_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        amt_lbl.setStyleSheet(f"color: {offer['color']}; border: none;")
        
        if num_active > 0:
            costs_txt = f"Total: ${actual_total:,.2f}\n(Base: ${base_total:,.2f} + Penalty: ${penalty_cost:,.2f})"
            rate_txt = f"{adjusted_interest*100:.1f}% (+{num_active*75}% penalty)"
        else:
            costs_txt = f"Total to repay: ${actual_total:,.2f}"
            rate_txt = f"{adjusted_interest*100:.1f}%"

        info = QLabel(f"Term: {offer['months']} months\nRate: {rate_txt}\n{costs_txt}\nMonthly: ${monthly:,.2f}")
        info.setStyleSheet("color: white; border: none; font-size: 11px;")
        
        btn = QPushButton("TAKE LOAN")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"background: {border_color}; color: black; font-weight: bold; border-radius: 5px; height: 35px;")
        
        btn.clicked.connect(lambda ch, o=offer, ai=adjusted_interest: self.take_loan(o, ai))
        
        lay.addWidget(amt_lbl)
        lay.addWidget(info)
        lay.addStretch()
        lay.addWidget(btn)
        return card

    def refresh_view(self, save_data=None):
        if save_data: self.save_data = save_data
        
        while self.offers_layout.count():
            child = self.offers_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        base_offers = [
            {"id": "small", "amount": 10000, "months": 10, "interest": 0.10, "color": "#3498db"},
            {"id": "medium", "amount": 100000, "months": 48, "interest": 0.20, "color": "#f1c40f"},
            {"id": "large", "amount": 1000000, "months": 120, "interest": 0.35, "color": "#e74c3c"}
        ]

        for offer in base_offers:
            card = self.create_loan_offer_card(offer)
            self.offers_layout.addWidget(card)

        while self.loans_layout.count():
            child = self.loans_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        active_loans = self.save_data.get('active_loans', [])
        for i, loan in enumerate(active_loans):
            loan_widget = self.create_active_loan_widget(loan, i)
            self.loans_layout.addWidget(loan_widget)

    def create_active_loan_widget(self, loan, index):
        frame = QFrame()
        frame.setStyleSheet("background: #1a1a1a; border-radius: 10px; padding: 10px; margin-bottom: 5px;")
        lay = QHBoxLayout(frame)

        info_lay = QVBoxLayout()
        title = QLabel(f"<b>Loan: ${loan['principal']:,}</b>")
        title.setStyleSheet("color: white; border: none;")
        
        progress = QProgressBar()
        progress.setMaximum(int(loan['total_to_pay']))
        progress.setValue(int(loan['paid_amount']))
        progress.setStyleSheet("QProgressBar { height: 10px; background: #333; border-radius: 5px; } QProgressBar::chunk { background: #2ecc71; }")
        
        status = QLabel(f"Paid: ${loan['paid_amount']:,.2f} / ${loan['total_to_pay']:,.2f}")
        status.setStyleSheet("color: #888; border: none; font-size: 10px;")
        
        info_lay.addWidget(title)
        info_lay.addWidget(progress)
        info_lay.addWidget(status)
        lay.addLayout(info_lay, 2)

        repay_panel = QVBoxLayout()
        
        slider_lay = QHBoxLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(loan['remaining_months'])
        slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        val_lbl = QLabel(f"Pay 1 installment: ${loan['monthly_rate']:,.2f}")
        val_lbl.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 11px;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_val(val, l=loan, lbl=val_lbl):
            amt = val * l['monthly_rate']
            lbl.setText(f"Pay {val} installments: ${amt:,.2f}")

        slider.valueChanged.connect(update_val)
        
        repay_btn = QPushButton("CONFIRM REPAY")
        repay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        repay_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; border-radius: 4px; padding: 5px;")
        
        repay_btn.clicked.connect(lambda ch, s=slider, idx=index: self.repay_custom(idx, s.value()))

        repay_panel.addWidget(val_lbl)
        repay_panel.addWidget(slider)
        repay_panel.addWidget(repay_btn)
        lay.addLayout(repay_panel, 1)

        return frame

    def take_loan(self, offer, adjusted_interest):
        total_to_pay = offer['amount'] * (1 + adjusted_interest)
        
        new_loan = {
            "type": offer['id'],
            "principal": offer['amount'],
            "total_to_pay": total_to_pay,
            "monthly_rate": total_to_pay / offer['months'],
            "remaining_months": offer['months'],
            "paid_amount": 0,
            "is_new": True
        }
        
        if 'active_loans' not in self.save_data: 
            self.save_data['active_loans'] = []
            
        self.save_data['active_loans'].append(new_loan)
        self.save_data['balance'] += offer['amount']
        
        self.parent_ctrl.log_transaction(
            "Bank", 
            f"Loan Taken: ${offer['amount']:,} (Rate: {adjusted_interest*100:.1f}%)", 
            offer['amount']
        )
        
        self.parent_ctrl.update_money_display()
        
        self.refresh_view() 
        
        QMessageBox.information(self, "Bank", f"Loan of ${offer['amount']:,} credited to your account.")

    def repay_early(self, idx):
        loan = self.save_data['active_loans'][idx]
        remaining = loan['total_to_pay'] - loan['paid_amount']
        
        if self.save_data.get('balance', 0) >= remaining:
            self.save_data['balance'] -= remaining
            self.save_data['active_loans'].pop(idx)
            self.parent_ctrl.log_transaction("Bank", "Early Loan Repayment", -remaining)
            self.parent_ctrl.update_money_display()
            self.refresh_view()
            QMessageBox.information(self, "Bank", "Loan repaid successfully!")
        else:
            QMessageBox.warning(self, "Bank", "Not enough money to repay this loan early!")

    def repay_custom(self, idx, num_installments):
        loan = self.save_data['active_loans'][idx]
        total_cost = num_installments * loan['monthly_rate']
        
        if self.save_data.get('balance', 0) >= total_cost:
            self.save_data['balance'] -= total_cost
            
            loan['paid_amount'] += total_cost
            loan['remaining_months'] -= num_installments
            
            
            self.parent_ctrl.log_transaction("Bank", f"Extra Repayment ({num_installments} inst.)", -total_cost)
            
            if loan['remaining_months'] <= 0:
                self.save_data['active_loans'].pop(idx)
                QMessageBox.information(self, "Bank", "Loan fully repaid!")
            else:
                QMessageBox.information(self, "Bank", f"Successfully paid {num_installments} installments.")
            
            self.parent_ctrl.update_money_display()
            self.refresh_view()
        else:
            QMessageBox.warning(self, "Bank", "Not enough money for this repayment!")