import sys
import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QSplitter, QGroupBox
)

from core.segmentation import detect_points, detect_lines, detect_edges, colorize_segments
from core.thresholding import global_threshold_otsu, global_threshold_entropy

class ScalableImageLabel(QLabel):
    """Метка для автоматического пропорционального масштабирования изображения."""
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.pixmap_orig = None
        self.setMinimumSize(180, 180)

    def set_image(self, pixmap):
        self.pixmap_orig = pixmap
        self.update_scaled_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scaled_image()

    def update_scaled_image(self):
        if self.pixmap_orig and not self.pixmap_orig.isNull():
            scaled = self.pixmap_orig.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            super().setPixmap(scaled)

class Lab2App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №2 — Компьютерная графика (Вариант 9)")
        self.setMinimumSize(1200, 700)
        
        self.current_image = None
        self.processed_image = None
        self.colored_image = None
        
        self.init_ui()
        self.load_default_image()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 1. Левая панель управления
        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(12)
        
        self.btn_load = QPushButton("Загрузить изображение...")
        self.btn_load.setFixedHeight(36)
        self.btn_load.clicked.connect(self.load_image_file)
        control_layout.addWidget(self.btn_load)
        
        # Группа сегментации
        seg_group = QGroupBox("Сегментация (Точки/Линии/Границы)")
        seg_layout = QVBoxLayout(seg_group)
        
        self.combo_seg_method = QComboBox()
        self.combo_seg_method.addItems([
            "Обнаружение точек (Лапласиан)",
            "Линии: Горизонтальные",
            "Линии: Вертикальные",
            "Линии: Диагональ (+43°)",
            "Линии: Диагональ (135°)",
            "Перепады яркости (Границы Собеля)"
        ])
        seg_layout.addWidget(self.combo_seg_method)
        
        self.btn_apply_seg = QPushButton("Применить сегментацию")
        self.btn_apply_seg.setFixedHeight(32)
        self.btn_apply_seg.clicked.connect(self.apply_segmentation)
        seg_layout.addWidget(self.btn_apply_seg)
        control_layout.addWidget(seg_group)
        
        # Группа пороговой обработки
        thresh_group = QGroupBox("Глобальная пороговая обработка")
        thresh_layout = QVBoxLayout(thresh_group)
        
        self.combo_thresh_method = QComboBox()
        self.combo_thresh_method.addItems([
            "Метод Отсу (Otsu)",
            "Метод на основе энтропии (Kapur)"
        ])
        thresh_layout.addWidget(self.combo_thresh_method)
        
        self.btn_apply_thresh = QPushButton("Выполнить бинаризацию")
        self.btn_apply_thresh.setFixedHeight(32)
        self.btn_apply_thresh.clicked.connect(self.apply_thresholding)
        thresh_layout.addWidget(self.btn_apply_thresh)
        
        control_layout.addWidget(thresh_group)
        
        self.info_label = QLabel("Статус: Ожидание действия")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        control_layout.addWidget(self.info_label)
        
        control_layout.addStretch()
        main_layout.addWidget(control_panel)
        
        # 2. Правая область: Сплиттер на ТРИ экрана
        images_splitter = QSplitter(Qt.Horizontal)
        
        # Экран 1: Оригинал
        orig_container = QWidget()
        orig_layout = QVBoxLayout(orig_container)
        orig_layout.setContentsMargins(0, 0, 0, 0)
        orig_layout.addWidget(QLabel("<b>1. Оригинал:</b>"))
        self.lbl_original = ScalableImageLabel()
        self.lbl_original.setStyleSheet("background-color: #232323; border: 1px solid #333333; border-radius: 4px;")
        orig_layout.addWidget(self.lbl_original)
        images_splitter.addWidget(orig_container)
        
        # Экран 2: Результат обработки
        res_container = QWidget()
        res_layout = QVBoxLayout(res_container)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.addWidget(QLabel("<b>2. Результат обработки:</b>"))
        self.lbl_result = ScalableImageLabel()
        self.lbl_result.setStyleSheet("background-color: #232323; border: 1px solid #333333; border-radius: 4px;")
        res_layout.addWidget(self.lbl_result)
        images_splitter.addWidget(res_container)
        
        # Экран 3: Цветные сегменты
        col_container = QWidget()
        col_layout = QVBoxLayout(col_container)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.addWidget(QLabel("<b>3. Сегменты (цветами):</b>"))
        self.lbl_colored = ScalableImageLabel()
        self.lbl_colored.setStyleSheet("background-color: #232323; border: 1px solid #333333; border-radius: 4px;")
        col_layout.addWidget(self.lbl_colored)
        images_splitter.addWidget(col_container)
        
        main_layout.addWidget(images_splitter, stretch=1)

    def load_default_image(self):
        dummy = np.ones((300, 300, 3), dtype=np.uint8) * 200
        cv2.putText(dummy, "TEST IMAGE", (45, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 50, 50), 2)
        cv2.circle(dummy, (150, 80), 30, (20, 20, 20), -1)
        cv2.rectangle(dummy, (80, 200), (220, 240), (100, 100, 100), -1)
        self.current_image = dummy
        self.processed_image = dummy.copy()
        self.colored_image = colorize_segments(dummy)
        self.display_images()

    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", "Image Files (*.png *.jpg *.bmp *.tif)"
        )
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.current_image = img
                self.processed_image = img.copy()
                self.colored_image = colorize_segments(img)
                self.display_images()
                self.info_label.setText(f"Загружено: {file_path.split('/')[-1]}")

    def display_images(self):
        if self.current_image is not None:
            self.lbl_original.set_image(self.numpy_to_qpixmap(self.current_image))
        if self.processed_image is not None:
            self.lbl_result.set_image(self.numpy_to_qpixmap(self.processed_image))
        if self.colored_image is not None:
            self.lbl_colored.set_image(self.numpy_to_qpixmap(self.colored_image))

    def numpy_to_qpixmap(self, img_np):
        if len(img_np.shape) == 2:
            height, width = img_np.shape
            q_img = QImage(img_np.data, width, height, width, QImage.Format_Grayscale8)
        else:
            height, width, _ = img_np.shape
            bytes_per_line = 3 * width
            rgb_img = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def apply_segmentation(self):
        if self.current_image is None:
            return
        idx = self.combo_seg_method.currentIndex()
        
        if idx == 0:
            self.processed_image = detect_points(self.current_image)
            self.info_label.setText("Сегментация: обнаружение точек (Лапласиан)")
        elif idx == 1:
            self.processed_image = detect_lines(self.current_image, 'horizontal')
            self.info_label.setText("Сегментация: горизонтальные линии")
        elif idx == 2:
            self.processed_image = detect_lines(self.current_image, 'vertical')
            self.info_label.setText("Сегментация: вертикальные линии")
        elif idx == 3:
            self.processed_image = detect_lines(self.current_image, 'diag_43')
            self.info_label.setText("Сегментация: диагональные линии (+43°)")
        elif idx == 4:
            self.processed_image = detect_lines(self.current_image, 'diag_135')
            self.info_label.setText("Сегментация: диагональные линии (135°)")
        elif idx == 5:
            self.processed_image = detect_edges(self.current_image)
            self.info_label.setText("Сегментация: перепады яркости (Собель)")
            
        self.colored_image = colorize_segments(self.processed_image)
        self.display_images()

    def apply_thresholding(self):
        if self.current_image is None:
            return
        idx = self.combo_thresh_method.currentIndex()
        
        if idx == 0:
            res, t_val = global_threshold_otsu(self.current_image)
            self.processed_image = res
            self.info_label.setText(f"Метод Отсу. Порог T = {t_val:.1f}")
        elif idx == 1:
            res, t_val = global_threshold_entropy(self.current_image)
            self.processed_image = res
            self.info_label.setText(f"Метод энтропии (Kapur). Порог T = {t_val:.1f}")
            
        self.colored_image = colorize_segments(self.processed_image)
        self.display_images()

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
    
    window = Lab2App()
    window.show()
    sys.exit(app.exec())