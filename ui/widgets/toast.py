from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve

class AchievementToast(QFrame):
    def __init__(self, parent, title, desc):
        super().__init__(parent)
        self.setFixedSize(300, 80)
        self.setFixedSize(300, 80)
        self.setStyleSheet("""
            QFrame {
                background-color: #1e272e;
                border: 2px solid #f1c40f;
                border-radius: 12px;
            }
            QLabel { color: white; border: none; background: transparent; }
        """)
        
        layout = QVBoxLayout(self)
        t = QLabel(f"🏆 NEW ACHIEVEMENT")
        t.setStyleSheet("font-weight: bold; color: #f1c40f; font-size: 12px;")
        
        n = QLabel(title)
        n.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        
        d = QLabel(desc)
        d.setStyleSheet("font-size: 10px; color: #aaaaaa;")
        d.setWordWrap(True)
        
        layout.addWidget(t)
        layout.addWidget(n)
        layout.addWidget(d)

        self.start_pos = QPoint(parent.width(), 120)
        self.end_pos = QPoint(parent.width() - 320, 120)
        self.move(self.start_pos)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setStartValue(self.start_pos)
        self.anim.setEndValue(self.end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        QTimer.singleShot(5000, self.fadeOut)

    def fadeOut(self):
        self.anim_back = QPropertyAnimation(self, b"pos")
        self.anim_back.setDuration(500)
        self.anim_back.setStartValue(self.pos())
        self.anim_back.setEndValue(QPoint(self.parent().width(), 120))
        self.anim_back.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_back.finished.connect(self.close)
        self.anim_back.start()
    
    def set_target_y(self, target_y):
        """Ustawia pozycję docelową i uruchamia animację wjazdu."""
        parent_width = self.parent().width()
        
        self.start_pos = QPoint(parent_width, target_y)
        self.end_pos = QPoint(parent_width - 320, target_y)
        self.move(self.start_pos)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setStartValue(self.start_pos)
        self.anim.setEndValue(self.end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        QTimer.singleShot(5000, self.fadeOut)