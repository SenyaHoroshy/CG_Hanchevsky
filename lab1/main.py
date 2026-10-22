import sys
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame, QLineEdit, QSlider, QSizePolicy, QFileDialog
)

from core.conversions import (
    rgb_to_cmyk, cmyk_to_rgb,
    rgb_to_hsv, hsv_to_rgb,
    rgb_to_hls, hls_to_rgb
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
        
        self.current_file_path = None  # путь к текущему файлу сохранения
        self.inputs_visible = False     # видимость полей точных значений около ползунков
        
        # списки для ползунков и полей ввода точных значений
        self.sliders_list = []
        self.exact_inputs_list = []
        
        # верхнее меню
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        file_menu = menubar.addMenu("Файл")
        
        new_action = QAction("Новая палитра", self)
        new_action.triggered.connect(self.new_palette)
        file_menu.addAction(new_action)
        
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self.open_palette)
        file_menu.addAction(open_action)
        
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_palette)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Сохранить как...", self)
        save_as_action.triggered.connect(self.save_palette_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
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
            
        # заголовки строк и ячейки палитры
        self.palette_buttons = []
        self.palette_colors = {}  # словарик для хранения цветов ячеек (r, g, b)
        self.selected_btn = None   # текущая выбранная ячейка
        
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
                
                # изначально все ячейки черные
                self.palette_colors[btn] = (0, 0, 0)
                btn.setStyleSheet(
                    "background-color: #000000;"
                    "border: 1px solid #2A2A2A;"
                    "border-radius: 0px;"
                )
                # подключаем клик по ячейке палитры
                btn.clicked.connect(lambda checked=False, b=btn: self.select_palette_cell(b))
                
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
        
        sliders_layout.addWidget(self.components_container, stretch=1)
        
        # квадратная кнопка с иконкой меню (≡) для открытия точных значений
        self.toggle_inputs_btn = QPushButton("≡")
        self.toggle_inputs_btn.setFixedSize(36, 36)
        self.toggle_inputs_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #C6C6C6;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        self.toggle_inputs_btn.clicked.connect(self.toggle_exact_inputs)
        sliders_layout.addWidget(self.toggle_inputs_btn, alignment=Qt.AlignVCenter)
        
        self.update_model_view(initial_model)
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
        
        # текущий цвет rgb выбранной ячейки
        self.current_rgb = (0, 0, 0)
        
        # выбираем первую ячейку по умолчанию
        if self.palette_buttons:
            self.select_palette_cell(self.palette_buttons[0])

    def new_palette(self):
        # очищаем палитру и сбрасываем путь
        self.current_file_path = None
        for btn in self.palette_buttons:
            self.palette_colors[btn] = (0, 0, 0)
            self.update_button_style(btn, 0, 0, 0)
        if self.palette_buttons:
            self.select_palette_cell(self.palette_buttons[0])

    def open_palette(self):
        # диалог выбора файла для открытия
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть палитру", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                # читаем и применяем цвета к ячейкам палитры
                for i, btn in enumerate(self.palette_buttons):
                    if i < len(lines):
                        _, r, g, b = self.parse_hex(lines[i])
                        self.palette_colors[btn] = (r, g, b)
                        self.update_button_style(btn, r, g, b)
                    else:
                        self.palette_colors[btn] = (0, 0, 0)
                        self.update_button_style(btn, 0, 0, 0)
                
                self.current_file_path = file_path
                if self.palette_buttons:
                    self.select_palette_cell(self.palette_buttons[0])
            except Exception as e:
                print(f"ошибка при открытии файла: {e}")

    def save_palette(self):
        # сохраняем по текущему пути
        if not self.current_file_path:
            self.save_palette_as()
        else:
            self._write_palette_to_file(self.current_file_path)

    def save_palette_as(self):
        # диалог сохранения файла
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить палитру", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            if not file_path.lower().endswith('.txt'):
                file_path += '.txt'
            self.current_file_path = file_path
            self._write_palette_to_file(self.current_file_path)

    def _write_palette_to_file(self, path):
        # запись hex-значений ячеек в файл
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for btn in self.palette_buttons:
                    r, g, b = self.palette_colors[btn]
                    hex_val = f"{r:02x}{g:02x}{b:02x}"
                    f.write(hex_val + "\n")
        except Exception as e:
            print(f"ошибка при сохранении файла: {e}")

    def update_button_style(self, btn, r, g, b):
        hex_c = f"#{r:02x}{g:02x}{b:02x}"
        if btn == self.selected_btn:
            border_style = "border: 2px solid #ffffff;"
        else:
            border_style = "border: 1px solid #2A2A2A;"
        
        btn.setStyleSheet(
            f"background-color: {hex_c};"
            f"{border_style}"
            "border-radius: 0px;"
        )

    def select_palette_cell(self, btn):
        old_btn = self.selected_btn
        self.selected_btn = btn
        
        # обновление палитры
        if old_btn and old_btn in self.palette_colors:
            r_old, g_old, b_old = self.palette_colors[old_btn]
            self.update_button_style(old_btn, r_old, g_old, b_old)
            
        r, g, b = self.palette_colors[btn]
        self.update_button_style(btn, r, g, b)
        
        # синхронизируем нижнее поле
        self.current_rgb = (r, g, b)
        
        if not self.is_hex_mode:
            self.color_input.setText(f"{r} {g} {b}")
        else:
            self.color_input.setText(f"{r:02x}{g:02x}{b:02x}")
        self.update_preview_color(r, g, b)
        self.update_sliders_from_rgb(r, g, b)

    def switch_color_model(self):
        self.current_model_idx = (self.current_model_idx + 1) % len(self.model_names)
        model_name = self.model_names[self.current_model_idx]
        self.update_model_view(model_name)
        
        r, g, b = self.current_rgb
        self.update_sliders_from_rgb(r, g, b)

    def toggle_exact_inputs(self):
        # переключение видимости полей точных значений
        self.inputs_visible = not self.inputs_visible
        for inp in self.exact_inputs_list:
            inp.setVisible(self.inputs_visible)

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
                
        self.sliders_list.clear()
        self.exact_inputs_list.clear()
        
        for i, letter in enumerate(letters):
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(8)
            
            slider = QSlider(Qt.Horizontal)
            is_float_slider = False
            
            if model_name == "RGB":
                slider.setRange(0, 255)
            elif model_name == "CMYK":
                slider.setRange(0, 1000)
                is_float_slider = True
            elif model_name in ("HSV", "HLS"):
                if letter == "H":
                    slider.setRange(0, 360)
                else:
                    slider.setRange(0, 100)
                    is_float_slider = True
                    
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
            
            default_text = "0.00" if is_float_slider else "0"
            exact_input = QLineEdit(default_text)
            exact_input.setFixedWidth(55)
            exact_input.setFixedHeight(26)
            exact_input.setAlignment(Qt.AlignCenter)
            exact_input.setVisible(self.inputs_visible)
            exact_input.setStyleSheet(
                "background-color: #1a1a1a;"
                "color: #C6C6C6;"
                "border: 1px solid #2A2A2A;"
                "border-radius: 3px;"
                "font-size: 11px;"
            )
            
            slider.valueChanged.connect(lambda val, s=slider, inp=exact_input, f=is_float_slider: self.on_slider_changed(s, inp, f))
            exact_input.editingFinished.connect(lambda s=slider, inp=exact_input, f=is_float_slider: self.on_exact_input_finished(s, inp, f))
            
            row_l.addWidget(slider, stretch=1)
            row_l.addWidget(exact_input)
            
            self.components_layout.addWidget(row_w)
            self.sliders_list.append(slider)
            self.exact_inputs_list.append(exact_input)

    def on_slider_changed(self, slider, exact_input, is_float):
        val = slider.value()
        if is_float:
            if slider.maximum() == 1000:
                f_val = val / 1000.0
            else:
                f_val = val / 100.0
            exact_input.setText(f"{f_val:.2f}")
        else:
            exact_input.setText(str(val))
        self.update_color_from_sliders()

    def on_exact_input_finished(self, slider, exact_input, is_float):
        text = exact_input.text().replace(',', '.')
        try:
            num = float(text)
            if is_float:
                num = max(0.0, min(1.0, num))
                if slider.maximum() == 1000:
                    slider.setValue(int(round(num * 1000)))
                else:
                    slider.setValue(int(round(num * 100)))
                exact_input.setText(f"{num:.2f}")
            else:
                num = int(round(num))
                num = max(slider.minimum(), min(slider.maximum(), num))
                slider.setValue(num)
                exact_input.setText(str(num))
        except ValueError:
            if is_float:
                if slider.maximum() == 1000:
                    exact_input.setText(f"{slider.value() / 1000.0:.2f}")
                else:
                    exact_input.setText(f"{slider.value() / 100.0:.2f}")
            else:
                exact_input.setText(str(slider.value()))

    def update_color_from_sliders(self):
        if not self.sliders_list:
            return
            
        model_name = self.model_names[self.current_model_idx]
        
        if model_name == "RGB":
            r = self.sliders_list[0].value()
            g = self.sliders_list[1].value()
            b = self.sliders_list[2].value()
        elif model_name == "CMYK":
            c = self.sliders_list[0].value() / 1000.0
            m = self.sliders_list[1].value() / 1000.0
            y = self.sliders_list[2].value() / 1000.0
            k = self.sliders_list[3].value() / 1000.0
            r, g, b = cmyk_to_rgb(c, m, y, k)
        elif model_name == "HSV":
            h = self.sliders_list[0].value()
            s = self.sliders_list[1].value() / 100.0
            v = self.sliders_list[2].value() / 100.0
            r, g, b = hsv_to_rgb(h, s, v)
        elif model_name == "HLS":
            h = self.sliders_list[0].value()
            l = self.sliders_list[1].value() / 100.0
            s = self.sliders_list[2].value() / 100.0
            r, g, b = hls_to_rgb(h, l, s)
        else:
            r, g, b = 0, 0, 0

        self.current_rgb = (r, g, b)
        self.update_preview_color(r, g, b)
        if not self.is_hex_mode:
            self.color_input.setText(f"{r} {g} {b}")
        else:
            self.color_input.setText(f"{r:02x}{g:02x}{b:02x}")
            
        if self.selected_btn and self.selected_btn in self.palette_colors:
            self.palette_colors[self.selected_btn] = (r, g, b)
            self.update_button_style(self.selected_btn, r, g, b)

    def update_sliders_from_rgb(self, r, g, b):
        if not self.sliders_list:
            return
            
        model_name = self.model_names[self.current_model_idx]
        
        for slider in self.sliders_list:
            slider.blockSignals(True)
            
        if model_name == "RGB":
            vals = [r, g, b]
            for i, val in enumerate(vals):
                self.sliders_list[i].setValue(val)
                if i < len(self.exact_inputs_list):
                    self.exact_inputs_list[i].setText(str(val))
        elif model_name == "CMYK":
            c, m, y, k = rgb_to_cmyk(r, g, b)
            vals = [c, m, y, k]
            for i, v in enumerate(vals):
                self.sliders_list[i].setValue(int(round(v * 1000)))
                if i < len(self.exact_inputs_list):
                    self.exact_inputs_list[i].setText(f"{v:.2f}")
        elif model_name == "HSV":
            h, s, v = rgb_to_hsv(r, g, b)
            vals = [int(round(h)), s, v]
            for i, v_val in enumerate(vals):
                if i == 0:
                    self.sliders_list[i].setValue(v_val)
                    if i < len(self.exact_inputs_list):
                        self.exact_inputs_list[i].setText(str(v_val))
                else:
                    self.sliders_list[i].setValue(int(round(v_val * 100)))
                    if i < len(self.exact_inputs_list):
                        self.exact_inputs_list[i].setText(f"{v_val:.2f}")
        elif model_name == "HLS":
            h, l, s = rgb_to_hls(r, g, b)
            vals = [int(round(h)), l, s]
            for i, v_val in enumerate(vals):
                if i == 0:
                    self.sliders_list[i].setValue(v_val)
                    if i < len(self.exact_inputs_list):
                        self.exact_inputs_list[i].setText(str(v_val))
                else:
                    self.sliders_list[i].setValue(int(round(v_val * 100)))
                    if i < len(self.exact_inputs_list):
                        self.exact_inputs_list[i].setText(f"{v_val:.2f}")
                
        for slider in self.sliders_list:
            slider.blockSignals(False)

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
        else:
            _, r, g, b = self.parse_hex(text)
            
        # обновляем превью
        self.current_rgb = (r, g, b)
        self.update_preview_color(r, g, b)
        
        # обновляем цвет на палитре
        if self.selected_btn and self.selected_btn in self.palette_colors:
            self.palette_colors[self.selected_btn] = (r, g, b)
            self.update_button_style(self.selected_btn, r, g, b)
            
        self.update_sliders_from_rgb(r, g, b)

    def apply_formatting_and_finish(self):
        text = self.color_input.text()
        if not self.is_hex_mode:
            r, g, b = self.parse_rgb(text)
            self.color_input.setText(f"{r} {g} {b}")
            self.update_preview_color(r, g, b)
            if self.selected_btn and self.selected_btn in self.palette_colors:
                self.palette_colors[self.selected_btn] = (r, g, b)
                self.update_button_style(self.selected_btn, r, g, b)
            self.update_sliders_from_rgb(r, g, b)
        else:
            clean_hex, r, g, b = self.parse_hex(text)
            self.color_input.setText(clean_hex)
            self.update_preview_color(r, g, b)
            if self.selected_btn and self.selected_btn in self.palette_colors:
                self.palette_colors[self.selected_btn] = (r, g, b)
                self.update_button_style(self.selected_btn, r, g, b)
            self.update_sliders_from_rgb(r, g, b)

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