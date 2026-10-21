import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame
)

class Lab1App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.setMinimumSize(650, 550)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # сетка палитры
        palette_container = QWidget()
        palette_layout = QGridLayout(palette_container)
        palette_layout.setSpacing(0)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        
        self.palette_buttons = []
        rows, cols = 4, 10
        
        for r in range(rows):
            for c in range(cols):
                btn = QPushButton()
                btn.setFixedSize(48, 48)
                btn.setStyleSheet(
                    "background-color: #000000;"
                    "border: 1px solid #000000;"
                )
                palette_layout.addWidget(btn, r, c)
                self.palette_buttons.append(btn)
                
        main_layout.addWidget(palette_container, alignment=Qt.AlignCenter)
        
        # панель настроек цвета снизу
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        
        # выбор цветовой модели (RGB, CMYK, HSV, HLS)
        model_selector_layout = QHBoxLayout()
        model_selector_layout.setSpacing(0)
        
        self.model_buttons = ["RGB", "CMYK", "HSV", "HLS"]
        self.model_btn_elements = []
        
        for model_name in self.model_buttons:
            m_btn = QPushButton(model_name)
            m_btn.setCheckable(True)
            m_btn.setFixedHeight(35)
            m_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    color: #cccccc;
                    border: 1px solid #3c3c3c;
                    border-radius: 0px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    color: white;
                    border: 1px solid #005999;
                    border-radius: 0px;
                }
            """)
            if model_name == "RGB":
                m_btn.setChecked(True)
                
            model_selector_layout.addWidget(m_btn)
            self.model_btn_elements.append(m_btn)
            
        controls_layout.addLayout(model_selector_layout)
        
        # заглушка под ползунки и поля ввода выбранной модели
        self.settings_placeholder = QLabel("здесь появятся настройки для выбранной модели", self)
        self.settings_placeholder.setAlignment(Qt.AlignCenter)
        self.settings_placeholder.setStyleSheet(
            "color: #777777; "
            "background-color: #181818; "
            "border: 1px dashed #333333; "
            "border-radius: 0px; "
            "padding: 30px;"
        )
        controls_layout.addWidget(self.settings_placeholder)
        
        main_layout.addLayout(controls_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(24, 24, 24))
    dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Button, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    app.setPalette(dark_palette)
    
    window = Lab1App()
    window.show()
    sys.exit(app.exec())