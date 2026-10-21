import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class Lab1App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1")
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # заглушка
        label = QLabel("тест", self)
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Lab1App()
    window.show()
    sys.exit(app.exec())