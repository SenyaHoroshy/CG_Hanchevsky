import sys
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame, QLineEdit, QSlider, QSizePolicy
)

class FormattedLineEdit(QLineEdit):
    def __init__(self, on_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_format = on_format
        self.returnPressed.connect(self.on_format)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.on_format:
            self.on_format()

class Lab1App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.setMinimumSize(600, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # сетка палитры
        palette_container = QWidget()
        palette_layout = QGridLayout(palette_container)
        palette_layout.setSpacing(0)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        
        # заголовок столбцов
        for c in range(10):
            col_lbl = QLabel(str(c))
            col_lbl.setAlignment(Qt.AlignCenter)
            col_lbl.setStyleSheet("color: #C6C6C6; font-size: 11px;")
            palette_layout.addWidget(col_lbl, 0, c + 1)
            
        # заголовки строк
        self.palette_buttons = []
        rows, cols = 4, 10
        
        for r in range(rows):
            row_lbl = QLabel(str(r))
            row_lbl.setAlignment(Qt.AlignCenter)
            row_lbl.setStyleSheet("color: #C6C6C6; font-size: 11px;")
            palette_layout.addWidget(row_lbl, r + 1, 0)
            
            for c in range(cols):
                btn = QPushButton()
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumSize(38, 44)
                btn.setStyleSheet(
                    "background-color: #000000;"
                    "border: 1px solid #2A2A2A;"
                    "border-radius: 0px;"
                )
                palette_layout.addWidget(btn, r + 1, c + 1)
                self.palette_buttons.append(btn)
                
        main_layout.addWidget(palette_container, stretch=1)
        
        # область ползунков
        sliders_container = QWidget()
        sliders_container.setFixedHeight(220)
        sliders_container.setFixedWidth(560)
        sliders_container.setStyleSheet(
            "background-color: #000000;"
            "border: none;"
            "border-radius: 6px;"
        )
        sliders_layout = QHBoxLayout(sliders_container)
        sliders_layout.setContentsMargins(8, 8, 8, 8)
        sliders_layout.setSpacing(10)
        
        # конфиги режимов и их букв
        self.model_configs = {
            "RGB": ["R", "G", "B"],
            "CMYK": ["C", "M", "Y", "K"],
            "HSV": ["H", "S", "V"],
            "HLS": ["H", "L", "S"]
        }
        self.model_names = list(self.model_configs.keys())
        self.current_model_idx = 0
        
        initial_model = self.model_names[self.current_model_idx]
        
        # вертикальная кнопка переключения режимов
        self.vertical_model_btn = QPushButton()
        self.vertical_model_btn.setFixedWidth(36)
        self.vertical_model_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.vertical_model_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #C6C6C6;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        self.vertical_model_btn.clicked.connect(self.switch_color_model)
        
        self.vertical_btn_layout = QVBoxLayout(self.vertical_model_btn)
        self.vertical_btn_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_btn_layout.setSpacing(4)
        
        sliders_layout.addWidget(self.vertical_model_btn)
        
        # область для ползунков
        self.components_container = QWidget()
        self.components_layout = QVBoxLayout(self.components_container)
        self.components_layout.setContentsMargins(0, 0, 0, 0)
        self.components_layout.setSpacing(8)
        
        self.update_model_view(initial_model)
        sliders_layout.addWidget(self.components_container, stretch=1)
        
        main_layout.addWidget(sliders_container, alignment=Qt.AlignCenter)
        
        # область для ввода RGB и HEX
        format_container = QWidget()
        format_container.setFixedHeight(36)
        format_container.setFixedWidth(560)
        format_container.setStyleSheet(
            "background-color: #000000;"
            "border: none;"
            "border-radius: 6px;"
        )
        format_layout = QHBoxLayout(format_container)
        format_layout.setContentsMargins(3, 3, 3, 3)
        format_layout.setSpacing(4)
        
        # маленький квадратик предпросмотра
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet(
            "background-color: #ffffff;"
            "border-radius: 5px;"
        )
        format_layout.addWidget(self.color_preview)
        
        # кастомное поле ввода
        self.color_input = FormattedLineEdit(self.apply_formatting_and_finish, "0 0 0")
        self.color_input.setFixedHeight(30)
        self.color_input.setAlignment(Qt.AlignCenter)
        self.color_input.setStyleSheet(
            "background-color: #000000;"
            "color: #C6C6C6;"
            "border: none;"
            "padding: 0 5px;"
            "font-size: 13px;"
        )
        self.color_input.textEdited.connect(self.handle_text_edit)
        format_layout.addWidget(self.color_input, stretch=1)
        
        self.is_hex_mode = False
        
        # кнопка переключения формата (между RGB и HEX)
        self.format_toggle_btn = QPushButton("HEX")
        self.format_toggle_btn.setFixedSize(50, 30)
        self.format_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #C6C6C6;
                border: none;
                border-radius: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        self.format_toggle_btn.clicked.connect(self.toggle_color_format)
        format_layout.addWidget(self.format_toggle_btn)
        
        main_layout.addWidget(format_container, alignment=Qt.AlignCenter)
        
        self.update_preview_color(0, 0, 0)

    def switch_color_model(self):
        self.current_model_idx = (self.current_model_idx + 1) % len(self.model_names)
        model_name = self.model_names[self.current_model_idx]
        self.update_model_view(model_name)

    def update_model_view(self, model_name):
        letters = self.model_configs[model_name]
        
        while self.vertical_btn_layout.count():
            item = self.vertical_btn_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for letter in letters:
            lbl = QLabel(letter)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #C6C6C6; font-weight: bold; font-size: 13px; background: transparent;")
            self.vertical_btn_layout.addWidget(lbl)

        while self.components_layout.count():
            item = self.components_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for _ in letters:
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(8)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 5px;
                    background: #1e1e1e;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #C6C6C6;
                    width: 14px;
                    height: 14px;
                    margin: -5px 0;
                    border-radius: 7px;
                }
                QSlider::handle:horizontal:hover {
                    background: #ffffff;
                }
            """)
            row_l.addWidget(slider)
            
            self.components_layout.addWidget(row_w)

    def update_preview_color(self, r, g, b):
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.setStyleSheet(
            f"background-color: {hex_color}; border-radius: 5px;"
        )

    def handle_text_edit(self, text):
        if self.is_hex_mode:
            lower_text = text.lower()
            if lower_text != text:
                cursor_pos = self.color_input.cursorPosition()
                self.color_input.setText(lower_text)
                self.color_input.setCursorPosition(cursor_pos)
        self.apply_color_from_input()

    def parse_rgb(self, text):
        raw_nums = re.findall(r'-?\d+', text)
        nums = [int(n) for n in raw_nums]
        clamped = [max(0, min(255, n)) for n in nums]
        
        if len(clamped) < 3:
            clamped.extend([0] * (3 - len(clamped)))
        elif len(clamped) > 3:
            clamped = clamped[:3]
            
        return clamped[0], clamped[1], clamped[2]

    def parse_hex(self, text):
        clean = text.lstrip('#').lower()
        clean = ''.join([c for c in clean if c in '0123456789abcdef'])
        
        if len(clean) < 6:
            clean = clean.ljust(6, '0')
        elif len(clean) > 6:
            clean = clean[:6]
            
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
        return clean, r, g, b

    def apply_color_from_input(self):
        text = self.color_input.text()
        if not self.is_hex_mode:
            r, g, b = self.parse_rgb(text)
            self.update_preview_color(r, g, b)
        else:
            _, r, g, b = self.parse_hex(text)
            self.update_preview_color(r, g, b)

    def apply_formatting_and_finish(self):
        text = self.color_input.text()
        if not self.is_hex_mode:
            r, g, b = self.parse_rgb(text)
            self.color_input.setText(f"{r} {g} {b}")
            self.update_preview_color(r, g, b)
        else:
            clean_hex, r, g, b = self.parse_hex(text)
            self.color_input.setText(clean_hex)
            self.update_preview_color(r, g, b)

    def toggle_color_format(self):
        text = self.color_input.text()
        if not self.is_hex_mode:
            r, g, b = self.parse_rgb(text)
            hex_val = f"{r:02x}{g:02x}{b:02x}"
            self.color_input.setText(hex_val)
            self.is_hex_mode = True
            self.format_toggle_btn.setText("RGB")
            self.update_preview_color(r, g, b)
        else:
            clean_hex, r, g, b = self.parse_hex(text)
            self.color_input.setText(f"{r} {g} {b}")
            self.is_hex_mode = False
            self.format_toggle_btn.setText("HEX")
            self.update_preview_color(r, g, b)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(0x3C, 0x3C, 0x3C))
    dark_palette.setColor(QPalette.WindowText, QColor(0xC6, 0xC6, 0xC6))
    dark_palette.setColor(QPalette.Base, QColor(0x2B, 0x2B, 0x2B))
    dark_palette.setColor(QPalette.AlternateBase, QColor(0x31, 0x31, 0x31))
    dark_palette.setColor(QPalette.Text, QColor(0xC6, 0xC6, 0xC6))
    dark_palette.setColor(QPalette.Button, QColor(0x2B, 0x2B, 0x2B))
    dark_palette.setColor(QPalette.ButtonText, QColor(0xC6, 0xC6, 0xC6))
    app.setPalette(dark_palette)
    
    window = Lab1App()
    window.show()
    sys.exit(app.exec())