import os
import json
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QDateEdit, QWidget, QScrollArea, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QDate


class NewGameWindow(QDialog):
    """Dialog for creating a new save and player profile with avatar selection."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.setWindowTitle("Start New Game")
        self.setFixedSize(800, 700)
        self.setModal(True)

        self.saves_dir = os.path.join(os.path.dirname(__file__), "..", "saves")
        os.makedirs(self.saves_dir, exist_ok=True)

        # === MAIN LAYOUT ===
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        # === LEFT PANEL ===
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(15)

        # === TITLE ===
        self.title = QLabel("Create New Game")
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.title)

        # === GAME MODE ===
        self.mode_lbl = QLabel("Game Mode:")
        form_layout.addWidget(self.mode_lbl)
        self.mode_box = QComboBox()
        self.mode_box.addItems(["Standard", "Realistic"])
        self.mode_box.currentTextChanged.connect(self.update_mode_description)
        form_layout.addWidget(self.mode_box)

        # === NAME ===
        self.fn_lbl = QLabel("First Name:")
        form_layout.addWidget(self.fn_lbl)
        self.first_name_input = QLineEdit()
        form_layout.addWidget(self.first_name_input)

        # === SURNAME ===
        self.sn_lbl = QLabel("Surname (Save Name):")
        form_layout.addWidget(self.sn_lbl)
        self.surname_input = QLineEdit()
        form_layout.addWidget(self.surname_input)

        # === DATE OF BIRTH ===
        self.dob_lbl = QLabel("Date of Birth:")
        form_layout.addWidget(self.dob_lbl)
        self.dob_picker = QDateEdit()
        self.dob_picker.setCalendarPopup(True)
        self.dob_picker.setDisplayFormat("yyyy-MM-dd")
        self.dob_picker.setDate(QDate(2000, 1, 1))
        self.dob_picker.dateChanged.connect(self.validate_age)
        form_layout.addWidget(self.dob_picker)

        # === AGE ERROR ===
        self.age_error = QLabel("")
        self.age_error.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.age_error.setStyleSheet("color: red;")
        form_layout.addWidget(self.age_error)

        # === GENDER ===
        self.gender_lbl = QLabel("Gender:")
        form_layout.addWidget(self.gender_lbl)
        self.gender_box = QComboBox()
        self.gender_box.addItems(["Male", "Female"])
        self.gender_box.currentTextChanged.connect(self.update_avatars)
        form_layout.addWidget(self.gender_box)

        # === AVATAR SECTION ===
        self.avatar_lbl = QLabel("Choose Your Avatar:")
        form_layout.addWidget(self.avatar_lbl)

        # Scroll area for avatars
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(160)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.avatar_container = QWidget()
        self.avatar_layout = QHBoxLayout(self.avatar_container)
        self.avatar_layout.setContentsMargins(10, 10, 10, 10)
        self.avatar_layout.setSpacing(15)

        self.scroll_area.setWidget(self.avatar_container)
        form_layout.addWidget(self.scroll_area)

        self.avatar_labels = []
        self.selected_avatar = None
        self.update_avatars()

        # === CONFIRM BUTTON ===
        self.start_button = QPushButton("Start Game")
        self.start_button.setFixedHeight(45)
        self.start_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.start_button.clicked.connect(self.create_save)
        form_layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # === RIGHT PANEL (MODE DESCRIPTION) ===
        desc_layout = QVBoxLayout()
        desc_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.desc_title = QLabel("Mode Description")
        self.desc_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.desc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_layout.addWidget(self.desc_title)

        self.desc_text = QLabel()
        self.desc_text.setWordWrap(True)
        self.desc_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.desc_text.setFont(QFont("Arial", 11))
        desc_layout.addWidget(self.desc_text)

        # === ADD TO MAIN LAYOUT ===
        main_layout.addLayout(form_layout, 2)
        main_layout.addLayout(desc_layout, 1)
        self.setLayout(main_layout)

        self.apply_theme()
        self.validate_age()
        self.update_mode_description("Standard")

    # === THEME ===
    def apply_theme(self):
        if not self.theme:
            return
        c = self.theme.get_colors()
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        for lbl in [
            self.title, self.mode_lbl, self.fn_lbl, self.sn_lbl,
            self.dob_lbl, self.gender_lbl, self.avatar_lbl,
            self.desc_title, self.desc_text
        ]:
            lbl.setStyleSheet(f"color: {c['text']};")

        field_style = (
            f"background: {'#2a2a2a' if self.theme.dark_mode else '#ffffff'};"
            f"color: {c['text']}; border: 1px solid {c['tile_border']};"
            f"border-radius: 6px; padding: 6px;"
        )
        self.first_name_input.setStyleSheet(f"QLineEdit {{{field_style}}}")
        self.surname_input.setStyleSheet(f"QLineEdit {{{field_style}}}")
        self.mode_box.setStyleSheet(f"QComboBox {{{field_style}}}")
        self.gender_box.setStyleSheet(f"QComboBox {{{field_style}}}")
        self.dob_picker.setStyleSheet(f"QDateEdit {{{field_style}}}")

        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['button_bg']};
                color: white;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {c['button_hover']}; }}
            QPushButton:pressed {{ background-color: {c['button_pressed']}; }}
        """)

    # === MODE DESCRIPTION ===
    def update_mode_description(self, mode):
        if mode == "Standard":
            text = (
                "<b>🧩 STANDARD MODE</b><br><br>"
                "A simulation-based gameplay where market conditions evolve randomly over time.<br><br>"
                "You can fast-forward time, test strategies, and experiment freely "
                "without real-world consequences."
            )
        else:
            text = (
                "<b>🌍 REALISTIC MODE</b><br><br>"
                "This mode connects to real-world market data using live APIs.<br><br>"
                "Your trades follow actual movements — realistic and unpredictable."
            )
        self.desc_text.setText(text)

    # === AGE VALIDATION ===
    def validate_age(self):
        dob = self.dob_picker.date().toPyDate()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            self.age_error.setText("⚠️ You must be at least 18 years old to play.")
            self.start_button.setEnabled(False)
            self.start_button.setStyleSheet("opacity: 0.5;")
        else:
            self.age_error.setText("")
            self.start_button.setEnabled(True)
            self.apply_theme()

    # === AVATAR HANDLING ===
    def update_avatars(self):
        """Display avatars with horizontal scroll."""
        for i in reversed(range(self.avatar_layout.count())):
            widget = self.avatar_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        gender = self.gender_box.currentText().lower()
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "assets", "avatars")
        os.makedirs(avatar_path, exist_ok=True)
        avatars = [f for f in os.listdir(avatar_path) if f.startswith(gender) and f.endswith(".png")]
        avatars.sort()

        self.selected_avatar = None
        self.avatar_labels = []

        for avatar_file in avatars:
            avatar_full_path = os.path.join(avatar_path, avatar_file)
            img_label = QLabel()
            pixmap = QPixmap(avatar_full_path)
            pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setStyleSheet("""
                QLabel {
                    border: 2px solid transparent;
                    border-radius: 10px;
                    padding: 4px;
                }
                QLabel:hover {
                    border: 2px solid #0078D7;
                    background-color: rgba(0, 120, 215, 0.1);
                }
            """)
            img_label.mousePressEvent = lambda e, f=avatar_file, l=img_label: self.select_avatar(f, l)
            self.avatar_labels.append(img_label)
            self.avatar_layout.addWidget(img_label)

        if self.avatar_labels:
            self.select_avatar(avatars[0], self.avatar_labels[0])

    def select_avatar(self, filename, label):
        self.selected_avatar = filename
        for lbl in self.avatar_labels:
            lbl.setStyleSheet("""
                QLabel {
                    border: 2px solid transparent;
                    border-radius: 10px;
                    padding: 4px;
                }
                QLabel:hover {
                    border: 2px solid #0078D7;
                    background-color: rgba(0, 120, 215, 0.1);
                }
            """)
        label.setStyleSheet("""
            QLabel {
                border: 3px solid #0078D7;
                border-radius: 10px;
                background-color: rgba(0, 120, 215, 0.15);
                padding: 4px;
            }
        """)

    # === SAVE CREATION ===
    def create_save(self):
        name = self.first_name_input.text().strip()
        surname = self.surname_input.text().strip()
        dob = self.dob_picker.date().toPyDate()
        mode = self.mode_box.currentText()
        gender = self.gender_box.currentText()
        selected_avatar = self.selected_avatar

        if not name or not surname:
            QMessageBox.warning(self, "Missing Data", "Please enter your name and save name.")
            return

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        save_data = {
            "player_name": name,
            "player_surname": surname,
            "player_age": age,
            "date_of_birth": str(dob),
            "gender": gender,
            "avatar": selected_avatar,
            "mode": mode,
            "balance": 10000,
            "knowledge_level": 1,
            "prestige": 1,
            "created": timestamp
        }

        filename = f"{surname}-{mode}-{datetime.now().strftime('%Y-%m-%d')}.json"
        save_path = os.path.join(self.saves_dir, filename)
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=4)

        self.theme.set_last_save(filename)
        QMessageBox.information(self, "Game Created", f"New game saved as:\n{filename}")
        self.close()
