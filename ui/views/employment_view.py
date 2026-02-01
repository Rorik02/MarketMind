import os, json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QPushButton, QScrollArea, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt

class EmploymentView(QFrame):
    def __init__(self, parent=None, theme=None, save_data=None):
        super().__init__(parent)
        self.parent_ctrl = parent
        self.theme = theme
        self.save_data = save_data or {}
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        header_container = QWidget()
        header_container.setFixedHeight(60)
        header = QHBoxLayout(header_container)
        header.setContentsMargins(0, 0, 0, 0)

        title = QLabel("💼 CAREER & EDUCATION")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; border: none;")
        
        self.back_btn = QPushButton("⬅️ Back to Home")
        self.back_btn.setFixedSize(140, 36)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #5d6d7e;
            }
            QPushButton:hover {
                background-color: #485e74;
            }
        """)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.safe_go_back)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.back_btn)
        
        self.main_layout.addWidget(header_container)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 2px solid #3d3d3d; 
                background: #1a1a1a; 
                border-radius: 8px;
                top: -1px; /* Łączy ramkę z aktywną zakładką */
            }
            QTabBar::tab {
                background: #2a2a2a;
                color: #aaaaaa;
                padding: 12px 30px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:hover {
                background: #333333;
                color: white;
            }
            QTabBar::tab:selected {
                background: #3a96dd; /* Twój charakterystyczny niebieski kolor */
                color: white;
                border: 1px solid #3a96dd;
                padding-bottom: 13px; /* Lekkie powiększenie aktywnej zakładki */
            }
        """)
        
        self.main_layout.addWidget(self.tabs)
        self.refresh_tabs()

    def safe_go_back(self):
        if hasattr(self.parent_ctrl, 'workspace_stack'):
            self.parent_ctrl.workspace_stack.setCurrentIndex(0)
        elif hasattr(self.parent_ctrl, 'return_to_home'):
            self.parent_ctrl.return_to_home()

    def load_data(self, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "..", "data", filename)
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def create_job_market(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        layout = QVBoxLayout(container)
        
        jobs = self.load_data("jobs.json")
        courses = self.load_data("courses.json")
        completed_courses = self.save_data.get('completed_courses', [])
        current_job_id = self.save_data.get('current_job')
        course_names = {c['id']: c['name'] for c in courses}

        for job in jobs:
            card = QFrame()
            card.setFixedHeight(120)
            card.setStyleSheet("background: #252525; border: 1px solid #444; border-radius: 10px;")
            card_lay = QHBoxLayout(card)

            info = QVBoxLayout()
            info.addWidget(QLabel(f"<b>{job['title']}</b>"))
            info.addWidget(QLabel(f"<font color='#aaaaaa'>{job['company']}</font>"))
            info.addWidget(QLabel(f"<font color='#2ecc71'>Salary: ${job['base_salary']:,}/mo</font>"))
            
            req_met = True
            if job['req_course']:
                pretty_name = course_names.get(job['req_course'], job['req_course'])
                if job['req_course'] not in completed_courses:
                    req_met = False
                    info.addWidget(QLabel(f"<font color='#e74c3c'>Required: {pretty_name}</font>"))

            btn = QPushButton("APPLY" if req_met else "LOCKED")
            btn.setFixedSize(100, 40)
            btn.setEnabled(req_met and job['id'] != current_job_id)
            
            if job['id'] == current_job_id:
                btn.setText("CURRENT")
                btn.setStyleSheet("background: #f1c40f; color: black; font-weight: bold;")
            elif req_met:
                btn.setStyleSheet("background: #3a96dd; color: white; font-weight: bold;")
            
            btn.clicked.connect(lambda ch, j=job: self.apply_for_job(j))
            card_lay.addLayout(info)
            card_lay.addStretch()
            card_lay.addWidget(btn)
            layout.addWidget(card)
        
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_education(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        layout = QVBoxLayout(container)
        
        courses = self.load_data("courses.json")
        completed = self.save_data.get('completed_courses', [])
        active = self.save_data.get('active_course')

        for crs in courses:
            card = QFrame()
            card.setFixedHeight(100)
            card.setStyleSheet("background: #252525; border: 1px solid #444; border-radius: 10px;")
            card_lay = QHBoxLayout(card)

            info = QVBoxLayout()
            info.addWidget(QLabel(f"<b>{crs['name']}</b>"))
            info.addWidget(QLabel(f"<font color='#aaaaaa'>Duration: {crs['days']} days | Cost: ${crs['cost']:,}</font>"))

            btn = QPushButton("START")
            btn.setFixedSize(100, 40)
            
            if crs['id'] in completed or (active and active['id'] == crs['id'] and active['remaining_hours'] <= 0):
                btn.setText("DONE")
                btn.setEnabled(False)
                btn.setStyleSheet("background: #27ae60; color: white;")
            elif active and active['id'] == crs['id']:
                days_left = max(0, active['remaining_hours'] // 24)
                btn.setText(f"{days_left}d left")
                btn.setEnabled(False)
                btn.setStyleSheet("background: #e67e22; color: white;")
            else:
                btn.setStyleSheet("background: #3a96dd; color: white; font-weight: bold;")
            
            btn.clicked.connect(lambda ch, c=crs: self.start_course(c))
            card_lay.addLayout(info)
            card_lay.addStretch()
            card_lay.addWidget(btn)
            layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def apply_for_job(self, job):
        self.save_data['current_job'] = job['id']
        self.save_data['job_months'] = 0
        QMessageBox.information(self, "Career", f"You are now working as {job['title']}!")
        self.refresh_tabs()

    def start_course(self, crs):
        if self.save_data.get('balance', 0) >= crs['cost']:
            if self.save_data.get('active_course'):
                QMessageBox.warning(self, "Education", "You are already in a course!")
                return
            
            cost = crs['cost']
            
            self.save_data['balance'] -= cost
            
            if hasattr(self.parent_ctrl, 'log_transaction'):
                self.parent_ctrl.log_transaction(
                    "Edukacja", 
                    f"Kurs: {crs['name']}", 
                    -cost
                )
            
            self.save_data['active_course'] = {
                "id": crs['id'], 
                "name": crs['name'], 
                "remaining_hours": crs['days'] * 24
            }
            
            self.parent_ctrl.update_money_display()
            self.refresh_tabs()
            
            QMessageBox.information(self, "Education", f"Enrolled in {crs['name']}!")
        else:
            QMessageBox.warning(self, "Bank", "Insufficient funds!")

    def refresh_tabs(self):
        curr = self.tabs.currentIndex()
        self.tabs.clear()
        self.tabs.addTab(self.create_job_market(), "Market")
        self.tabs.addTab(self.create_education(), "Education")
        if curr != -1: self.tabs.setCurrentIndex(curr)

    def apply_theme(self, colors):
        self.setStyleSheet(f"background-color: {colors['tile_bg']}; border-radius: 18px;")