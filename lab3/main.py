import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QWheelEvent

from core.rasterization import step_line, dda_line, bresenham_line, bresenham_circle

class RasterCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.scale = 25  # Размер одного пикселя в сетке
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = QPointF()
        
        self.pixels = []
        self.algorithm_name = "Пошаговый алгоритм"
        self.execution_time = 0.0

    def set_data(self, pixels, name, exec_time):
        self.pixels = pixels
        self.algorithm_name = name
        self.execution_time = exec_time
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        zoom_in = event.angleDelta().y() > 0
        if zoom_in:
            self.scale = min(self.scale + 2, 80)
        else:
            self.scale = max(self.scale - 2, 8)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.position() - self.last_mouse_pos
            self.offset_x += int(delta.x())
            self.offset_y += int(delta.y())
            self.last_mouse_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        width = self.width()
        height = self.height()
        
        # Заливка фона
        painter.fillRect(0, 0, width, height, QColor(245, 246, 248))
        
        # Центр координат с учетом панорамирования
        center_x = width // 2 + self.offset_x
        center_y = height // 2 + self.offset_y
        
        pen_grid = QPen(QColor(220, 224, 230), 1, Qt.SolidLine)
        pen_axis = QPen(QColor(50, 60, 80), 2, Qt.SolidLine)
        pen_text = QColor(90, 100, 115)
        
        painter.setFont(QFont("Segoe UI", 8))
        
        scale_int = int(self.scale)
        
        # Вертикальные линии сетки (принудительно переводим в int для range)
        start_x = int(center_x % scale_int)
        for x in range(start_x, width, scale_int):
            grid_x_idx = (x - center_x) // scale_int
            painter.setPen(pen_axis if grid_x_idx == 0 else pen_grid)
            painter.drawLine(x, 0, x, height)
            if grid_x_idx != 0 and scale_int >= 15:
                painter.setPen(pen_text)
                painter.drawText(x - 12, center_y + 15, str(grid_x_idx))

        # Горизонтальные линии сетки (принудительно переводим в int для range)
        start_y = int(center_y % scale_int)
        for y in range(start_y, height, scale_int):
            grid_y_idx = (center_y - y) // scale_int  # Инверсия Y для декартовой системы
            painter.setPen(pen_axis if grid_y_idx == 0 else pen_grid)
            painter.drawLine(0, y, width, y)
            if grid_y_idx != 0 and scale_int >= 15:
                painter.setPen(pen_text)
                painter.drawText(center_x + 8, y + 4, str(grid_y_idx))

        # Главные оси координат
        painter.setPen(pen_axis)
        painter.drawLine(0, center_y, width, center_y)
        painter.drawLine(center_x, 0, center_x, height)
        
        # Отрисовка растрированных пикселей
        for px, py in self.pixels:
            screen_x = center_x + px * scale_int
            screen_y = center_y - py * scale_int  # Инвертируем Y обратно для экрана
            
            painter.fillRect(
                int(screen_x + 1), 
                int(screen_y - scale_int + 1), 
                int(scale_int - 1), 
                int(scale_int - 1), 
                QColor(52, 152, 219, 200)
            )

        # Вывод информации в углу экрана
        painter.setPen(QColor(40, 40, 40))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(20, 30, f"Алгоритм: {self.algorithm_name}")
        painter.drawText(20, 50, f"Время выполнения: {self.execution_time:.4f} мс")
        painter.drawText(20, 70, f"Пикселей закрашено: {len(self.pixels)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №3: Базовые растровые алгоритмы")
        self.resize(1100, 750)
        
        main_layout = QHBoxLayout()
        
        # Левая панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(320)
        
        group_box = QGroupBox("Параметры алгоритма")
        form_layout = QFormLayout()
        
        self.combo_alg = QComboBox()
        self.combo_alg.addItems([
            "Пошаговый алгоритм",
            "Алгоритм ЦДА",
            "Алгоритм Брезенхема (отрезок)",
            "Алгоритм Брезенхема (окружность)"
        ])
        self.combo_alg.currentIndexChanged.connect(self.on_alg_changed)
        form_layout.addRow("Алгоритм:", self.combo_alg)
        
        # Поля ввода координат
        self.input_x1 = QLineEdit("0")
        self.input_y1 = QLineEdit("0")
        self.input_x2 = QLineEdit("10")
        self.input_y2 = QLineEdit("7")
        
        self.label_x1 = QLabel("X1:")
        self.label_y1 = QLabel("Y1:")
        self.label_x2 = QLabel("X2 / Радиус:")
        self.label_y2 = QLabel("Y2:")
        
        form_layout.addRow(self.label_x1, self.input_x1)
        form_layout.addRow(self.label_y1, self.input_y1)
        form_layout.addRow(self.label_x2, self.input_x2)
        form_layout.addRow(self.label_y2, self.input_y2)
        
        group_box.setLayout(form_layout)
        control_layout.addWidget(group_box)
        
        btn_draw = QPushButton("Растрировать")
        btn_draw.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        btn_draw.clicked.connect(self.calculate_and_draw)
        control_layout.addWidget(btn_draw)
        
        control_layout.addStretch()
        
        # Холст для отрисовки
        self.canvas = RasterCanvas()
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.calculate_and_draw()

    def on_alg_changed(self, index):
        if index == 3:  # Окружность
            self.label_x2.setText("Радиус (R):")
            self.label_y2.hide()
            self.input_y2.hide()
        else:
            self.label_x2.setText("X2:")
            self.label_y2.show()
            self.input_y2.show()

    def calculate_and_draw(self):
        try:
            alg_idx = self.combo_alg.currentIndex()
            x1 = int(self.input_x1.text())
            y1 = int(self.input_y1.text())
            
            if alg_idx == 3:
                r = int(self.input_x2.text())
                pixels, exec_time = bresenham_circle(x1, y1, r)
                name = "Брезенхем (окружность)"
            else:
                x2 = int(self.input_x2.text())
                y2 = int(self.input_y2.text())
                
                if alg_idx == 0:
                    pixels, exec_time = step_line(x1, y1, x2, y2)
                    name = "Пошаговый алгоритм"
                elif alg_idx == 1:
                    pixels, exec_time = dda_line(x1, y1, x2, y2)
                    name = "Алгоритм ЦДА"
                else:
                    pixels, exec_time = bresenham_line(x1, y1, x2, y2)
                    name = "Брезенхем (отрезок)"
                    
            self.canvas.set_data(pixels, name, exec_time)
        except ValueError:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())