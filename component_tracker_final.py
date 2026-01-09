import sys
import json
import os
import re
import random
import string
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ComponentTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.components = []
        self.verified_components = []
        self.scan_history = []
        self.qr_scan_history = []
        self.programs_file = 'programs.json'
        self.components_file = 'components.json'
        self.results_dir = 'results'
        self.qr_results_dir = 'qr_results'
        self.current_program = "Не выбрана"
        self.load_data()
        self.ensure_directories()
        self.init_ui()
        
    def ensure_directories(self):
        """Создание необходимых директорий"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        if not os.path.exists(self.qr_results_dir):
            os.makedirs(self.qr_results_dir)
            
    def load_data(self):
        """Загрузка данных из файлов"""
        if os.path.exists(self.programs_file):
            try:
                with open(self.programs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.programs = data
                    else:
                        self.programs = []
            except:
                self.programs = []
        else:
            self.programs = []
        
        if not self.programs:
            self.programs = ["Программа 1", "Программа 2", "Программа 3", "Программа 4"]
            
        if os.path.exists(self.components_file):
            try:
                with open(self.components_file, 'r', encoding='utf-8') as f:
                    self.components = json.load(f)
            except:
                self.components = []
        else:
            self.components = []
            
    def save_data(self):
        """Сохранение всех данных"""
        with open(self.programs_file, 'w', encoding='utf-8') as f:
            json.dump(self.programs, f, ensure_ascii=False, indent=2)
            
        with open(self.components_file, 'w', encoding='utf-8') as f:
            json.dump(self.components, f, ensure_ascii=False, indent=2)
            
    def init_ui(self):
        """Инициализация графического интерфейса"""
        self.setWindowTitle("Система прослеживаемости компонентов")
        self.setGeometry(100, 100, 1200, 800)
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Вкладка инженера
        self.engineer_tab = QWidget()
        self.init_engineer_tab()
        self.tab_widget.addTab(self.engineer_tab, "👨‍🔧 Инженер")
        
        # Вкладка оператора
        self.operator_tab = QWidget()
        self.init_operator_tab()
        self.tab_widget.addTab(self.operator_tab, "👨‍💼 Оператор")
        
        # Вкладка автоматического сканирования QR
        self.qr_scan_tab = QWidget()
        self.init_qr_scan_tab()
        self.tab_widget.addTab(self.qr_scan_tab, "🔢 Автосканирование QR")
        
        # Вкладка с историей
        self.history_tab = QWidget()
        self.init_history_tab()
        self.tab_widget.addTab(self.history_tab, "📊 История")
        
        # Панель статуса
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        font = QFont("Arial", 10)
        self.setFont(font)
        
    def init_engineer_tab(self):
        """Инициализация вкладки инженера"""
        layout = QVBoxLayout(self.engineer_tab)
        
        title_label = QLabel("👨‍🔧 ИНЖЕНЕР ПО ПЕРЕНАЛАДКЕ ЛИНИИ")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                text-align: center;
            }
        """)
        layout.addWidget(title_label)
        
        # Группа для выбора или ввода программы
        program_group = QGroupBox("Выбор или ввод программы производства")
        program_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        program_layout = QHBoxLayout()
        
        # Переключатель между выпадающим списком и вводом
        self.program_mode_combo = QComboBox()
        self.program_mode_combo.addItems(["Выбрать из списка", "Ввести вручную"])
        self.program_mode_combo.currentTextChanged.connect(self.on_program_mode_changed)
        
        # Выпадающий список программ
        program_label = QLabel("Текущая программа:")
        program_label.setStyleSheet("font-weight: bold;")
        self.program_combo = QComboBox()
        self.program_combo.addItems(self.programs)
        self.program_combo.currentTextChanged.connect(self.on_program_changed)
        
        # Поле для ввода программы вручную
        self.program_input = QLineEdit()
        self.program_input.setPlaceholderText("Введите название программы")
        self.program_input.textChanged.connect(self.on_program_manual_changed)
        self.program_input.setVisible(False)
        
        # Кнопка добавления новой программы
        self.add_program_btn = QPushButton("➕ Добавить программу")
        self.add_program_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.add_program_btn.clicked.connect(self.add_new_program)
        self.add_program_btn.setVisible(False)
        
        program_layout.addWidget(QLabel("Режим:"))
        program_layout.addWidget(self.program_mode_combo)
        program_layout.addWidget(program_label)
        program_layout.addWidget(self.program_combo)
        program_layout.addWidget(self.program_input)
        program_layout.addWidget(self.add_program_btn)
        program_layout.addStretch()
        
        program_group.setLayout(program_layout)
        layout.addWidget(program_group)
        
        # Группа для ввода компонента
        group_box = QGroupBox("Добавление компонента")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        code_label = QLabel("Код компонента (10 символов):")
        code_label.setStyleSheet("font-weight: bold;")
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(10)
        self.code_input.setPlaceholderText("Пример: 4-22-00013")
        form_layout.addWidget(code_label, 0, 0)
        form_layout.addWidget(self.code_input, 0, 1)
        
        batch_label = QLabel("Партия (5 символов):")
        batch_label.setStyleSheet("font-weight: bold;")
        self.batch_input = QLineEdit()
        self.batch_input.setMaxLength(5)
        self.batch_input.setPlaceholderText("Пример: 00001")
        form_layout.addWidget(batch_label, 1, 0)
        form_layout.addWidget(self.batch_input, 1, 1)
        
        quantity_label = QLabel("Количество на плату:")
        quantity_label.setStyleSheet("font-weight: bold;")
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100)
        self.quantity_input.setValue(1)
        form_layout.addWidget(quantity_label, 2, 0)
        form_layout.addWidget(self.quantity_input, 2, 1)
        
        self.add_btn = QPushButton("➕ Добавить компонент")
        self.add_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 12px;
                background-color: #2ecc71;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_btn.clicked.connect(self.add_component_engineer)
        form_layout.addWidget(self.add_btn, 3, 0, 1, 2)
        
        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        
        table_label = QLabel("📋 Список добавленных компонентов:")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(5)
        self.components_table.setHorizontalHeaderLabels(["Код", "Партия", "Кол-во", "Дата добавления", "Действия"])
        self.components_table.horizontalHeader().setStretchLastSection(True)
        self.components_table.setAlternatingRowColors(True)
        self.components_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.components_table)
        
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Очистить все")
        clear_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_components)
        button_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #34495e;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        save_btn.clicked.connect(self.save_data)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.update_components_table()
        
    def on_program_mode_changed(self, mode):
        """Переключение между выпадающим списком и вводом вручную"""
        if mode == "Выбрать из списка":
            self.program_combo.setVisible(True)
            self.program_input.setVisible(False)
            self.add_program_btn.setVisible(False)
            self.on_program_changed(self.program_combo.currentText())
        else:
            self.program_combo.setVisible(False)
            self.program_input.setVisible(True)
            self.add_program_btn.setVisible(True)
            self.program_input.setFocus()
            
    def add_new_program(self):
        """Добавление новой программы в список и сохранение"""
        program_name = self.program_input.text().strip()
        
        if not program_name:
            QMessageBox.warning(self, "Ошибка", "Введите название программы!")
            return
            
        if program_name in self.programs:
            QMessageBox.warning(self, "Ошибка", f"Программа '{program_name}' уже существует!")
            return
            
        self.programs.append(program_name)
        self.save_data()
        
        self.program_combo.addItem(program_name)
        self.current_program = program_name
        
        self.status_bar.showMessage(f"✅ Программа '{program_name}' добавлена и сохранена!")
        QMessageBox.information(self, "Успех", f"Программа '{program_name}' успешно добавлена!")
        
        self.program_input.clear()
        
        # Переключаемся обратно на режим списка
        self.program_mode_combo.setCurrentText("Выбрать из списка")
            
    def on_program_changed(self, program_name):
        """Обработка изменения программы из списка"""
        if program_name:
            self.current_program = program_name
            self.status_bar.showMessage(f"✅ Выбрана программа: {program_name}")
        
    def on_program_manual_changed(self, program_name):
        """Обработка ввода программы вручную"""
        self.current_program = program_name if program_name else "Не выбрана"
        if program_name:
            self.status_bar.showMessage(f"Введена программа: {program_name}")
        
    def init_operator_tab(self):
        """Инициализация вкладки оператора"""
        layout = QVBoxLayout(self.operator_tab)
        
        title_label = QLabel("👨‍💼 ОПЕРАТОР ЛИНИИ")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                text-align: center;
            }
        """)
        layout.addWidget(title_label)
        
        self.program_info_label = QLabel(f"Текущая программа: {self.current_program}")
        self.program_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(self.program_info_label)
        
        group_box = QGroupBox("Сканирование линейного штрих-кода")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        scan_layout = QVBoxLayout()
        
        barcode_label = QLabel("Введите или отсканируйте штрих-код (27 символов):")
        barcode_label.setStyleSheet("font-weight: bold;")
        self.barcode_input = QLineEdit()
        self.barcode_input.setMaxLength(27)
        self.barcode_input.setPlaceholderText("Пример: 4-22-000130000118122503000")
        self.barcode_input.returnPressed.connect(self.check_barcode)
        scan_layout.addWidget(barcode_label)
        scan_layout.addWidget(self.barcode_input)
        
        format_label = QLabel("Формат: 10 символов (код) + 5 символов (партия) + 12 символов (другая информация)")
        format_label.setStyleSheet("font-style: italic; color: #7f8c8d;")
        scan_layout.addWidget(format_label)
        
        self.check_btn = QPushButton("🔍 Проверить штрих-код")
        self.check_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.check_btn.clicked.connect(self.check_barcode)
        scan_layout.addWidget(self.check_btn)
        
        group_box.setLayout(scan_layout)
        layout.addWidget(group_box)
        
        self.result_frame = QFrame()
        self.result_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.result_frame.setMinimumHeight(100)
        self.result_frame.setVisible(False)
        
        result_layout = QVBoxLayout(self.result_frame)
        
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        result_layout.addWidget(self.result_label)
        
        self.details_label = QLabel()
        self.details_label.setAlignment(Qt.AlignCenter)
        self.details_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        result_layout.addWidget(self.details_label)
        
        layout.addWidget(self.result_frame)
        
        verified_label = QLabel("✅ Проверенные компоненты для установки:")
        verified_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(verified_label)
        
        self.verified_table = QTableWidget()
        self.verified_table.setColumnCount(3)
        self.verified_table.setHorizontalHeaderLabels(["Код", "Партия", "Количество"])
        self.verified_table.horizontalHeader().setStretchLastSection(True)
        self.verified_table.setAlternatingRowColors(True)
        self.verified_table.setMaximumHeight(150)
        layout.addWidget(self.verified_table)
        
        button_layout = QHBoxLayout()
        
        clear_scan_btn = QPushButton("Очистить поле")
        clear_scan_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_scan_btn.clicked.connect(self.clear_scan)
        button_layout.addWidget(clear_scan_btn)
        
        clear_verified_btn = QPushButton("Очистить проверенные")
        clear_verified_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #e67e22;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        clear_verified_btn.clicked.connect(self.clear_verified_components)
        button_layout.addWidget(clear_verified_btn)
        
        layout.addLayout(button_layout)
        
        stats_label = QLabel("📈 Статистика проверок:")
        stats_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(stats_label)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Штрих-код", "Результат", "Сообщение", "Время"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setMaximumHeight(200)
        layout.addWidget(self.stats_table)
        
    def init_qr_scan_tab(self):
        """Инициализация вкладки автоматического сканирования QR"""
        layout = QVBoxLayout(self.qr_scan_tab)
        
        title_label = QLabel("🔢 АВТОМАТИЧЕСКОЕ СКАНИРОВАНИЕ QR-КОДОВ")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                text-align: center;
            }
        """)
        layout.addWidget(title_label)
        
        self.qr_program_info_label = QLabel(f"Текущая программа: {self.current_program}")
        self.qr_program_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(self.qr_program_info_label)
        
        # Группа для выбора режима сканирования
        mode_group = QGroupBox("Режим сканирования")
        mode_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        mode_layout = QHBoxLayout()
        
        self.qr_mode_group = QButtonGroup()
        self.qr_auto_radio = QRadioButton("Автоматическое сканирование (генерация)")
        self.qr_manual_radio = QRadioButton("Сканирование со сканера (ввод вручную)")
        
        self.qr_auto_radio.setChecked(True)
        self.qr_auto_radio.toggled.connect(self.on_qr_mode_changed)
        
        self.qr_mode_group.addButton(self.qr_auto_radio)
        self.qr_mode_group.addButton(self.qr_manual_radio)
        
        mode_layout.addWidget(self.qr_auto_radio)
        mode_layout.addWidget(self.qr_manual_radio)
        mode_layout.addStretch()
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Панель управления
        control_group = QGroupBox("Управление сканированием")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #2ecc71;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_btn.setEnabled(False)
        
        self.scan_status_label = QLabel("Статус: Остановлено")
        self.scan_status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        
        self.scan_counter = 0
        self.scan_counter_label = QLabel("Сканировано: 0")
        self.scan_counter_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.scan_status_label)
        control_layout.addStretch()
        control_layout.addWidget(self.scan_counter_label)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Поле для ввода QR-кода со сканера
        manual_group = QGroupBox("Ввод QR-кода со сканера")
        manual_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        manual_group.setVisible(False)
        
        manual_layout = QVBoxLayout()
        
        manual_label = QLabel("Отсканируйте QR-код со сканера:")
        manual_label.setStyleSheet("font-weight: bold;")
        
        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("QR-код будет введен автоматически")
        self.qr_input.returnPressed.connect(self.on_qr_scanned_manual)
        
        manual_layout.addWidget(manual_label)
        manual_layout.addWidget(self.qr_input)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        self.manual_group = manual_group
        
        # Окно сканирования
        scan_group = QGroupBox("Окно сканирования")
        scan_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        
        scan_layout = QVBoxLayout()
        self.scan_display = QTextEdit()
        self.scan_display.setReadOnly(True)
        self.scan_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
        """)
        scan_layout.addWidget(self.scan_display)
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        history_label = QLabel("📋 История сканирований QR-кодов:")
        history_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(history_label)
        
        self.qr_history_table = QTableWidget()
        self.qr_history_table.setColumnCount(6)
        self.qr_history_table.setHorizontalHeaderLabels(["Дата", "Время", "Программа", "QR-код", "Компоненты", "Детали"])
        self.qr_history_table.horizontalHeader().setStretchLastSection(True)
        self.qr_history_table.setAlternatingRowColors(True)
        layout.addWidget(self.qr_history_table)
        
        history_btn_layout = QHBoxLayout()
        
        clear_qr_history_btn = QPushButton("🗑️ Очистить историю QR")
        clear_qr_history_btn.clicked.connect(self.clear_qr_history)
        
        export_qr_history_btn = QPushButton("📤 Экспорт истории QR")
        export_qr_history_btn.clicked.connect(self.export_qr_history)
        
        history_btn_layout.addWidget(clear_qr_history_btn)
        history_btn_layout.addWidget(export_qr_history_btn)
        history_btn_layout.addStretch()
        
        layout.addLayout(history_btn_layout)
        
        self.start_btn.clicked.connect(self.start_qr_scanning)
        self.stop_btn.clicked.connect(self.stop_qr_scanning)
        
        self.is_scanning = False
        
    def on_qr_mode_changed(self):
        """Переключение между режимами QR сканирования"""
        if self.qr_auto_radio.isChecked():
            self.manual_group.setVisible(False)
            self.qr_input.clear()
        else:
            self.manual_group.setVisible(True)
            if self.is_scanning:
                self.stop_qr_scanning()
            self.qr_input.setFocus()
            
    def on_qr_scanned_manual(self):
        """Обработка ввода QR-кода со сканера вручную"""
        qr_code = self.qr_input.text().strip()
        
        if not qr_code:
            QMessageBox.warning(self, "Ошибка", "QR-код не может быть пустым!")
            return
        
        self.process_qr_code(qr_code)
        self.qr_input.clear()
        self.qr_input.setFocus()
        
    def init_history_tab(self):
        """Инициализация вкладки истории"""
        layout = QVBoxLayout(self.history_tab)
        
        title_label = QLabel("📊 ИСТОРИЯ СКАНИРОВАНИЙ")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                text-align: center;
            }
        """)
        layout.addWidget(title_label)
        
        filter_layout = QHBoxLayout()
        
        date_label = QLabel("Дата:")
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        
        status_label = QLabel("Статус:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "Успешно", "Ошибка"])
        
        filter_btn = QPushButton("Применить фильтр")
        filter_btn.clicked.connect(self.filter_history)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["ID", "Штрих-код", "Результат", "Сообщение", "Время"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Экспорт в CSV")
        export_btn.clicked.connect(self.export_history)
        
        clear_history_btn = QPushButton("🗑️ Очистить историю")
        clear_history_btn.clicked.connect(self.clear_history)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(clear_history_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.update_history_table()
        
    def add_component_engineer(self):
        """Добавление компонента инженером"""
        code = self.code_input.text().strip()
        batch = self.batch_input.text().strip()
        quantity = self.quantity_input.value()
        
        if len(code) != 10:
            QMessageBox.warning(self, "Ошибка", "Код компонента должен содержать 10 символов!")
            return
            
        if len(batch) != 5:
            QMessageBox.warning(self, "Ошибка", "Партия должна содержать 5 символов!")
            return
            
        for comp in self.components:
            if comp['code'] == code and comp['batch'] == batch:
                reply = QMessageBox.question(
                    self, "Подтверждение",
                    f"Компонент с кодом {code} и партией {batch} уже существует.\nОбновить количество?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    comp['quantity'] = quantity
                    self.update_components_table()
                    self.status_bar.showMessage(f"Обновлен компонент: {code}, партия: {batch}")
                return
        
        component = {
            'id': len(self.components) + 1,
            'code': code,
            'batch': batch,
            'quantity': quantity,
            'added_date': datetime.now().isoformat()
        }
        
        self.components.append(component)
        self.update_components_table()
        self.status_bar.showMessage(f"Добавлен компонент: {code}, партия: {batch}, количество: {quantity}")
        
        self.code_input.clear()
        self.batch_input.clear()
        self.quantity_input.setValue(1)
        
    def update_components_table(self):
        """Обновление таблицы компонентов"""
        self.components_table.setRowCount(len(self.components))
        
        for row, component in enumerate(self.components):
            self.components_table.setItem(row, 0, QTableWidgetItem(component['code']))
            self.components_table.setItem(row, 1, QTableWidgetItem(component['batch']))
            self.components_table.setItem(row, 2, QTableWidgetItem(str(component['quantity'])))
            
            try:
                dt = datetime.fromisoformat(component['added_date'])
                date_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = component['added_date']
            self.components_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            delete_btn = QPushButton("Удалить")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_component(r))
            self.components_table.setCellWidget(row, 4, delete_btn)
            
    def delete_component(self, row):
        """Удаление компонента"""
        if 0 <= row < len(self.components):
            component = self.components[row]
            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Удалить компонент {component['code']}, партия {component['batch']}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.components[row]
                self.update_components_table()
                self.status_bar.showMessage("Компонент удален")
                
    def clear_all_components(self):
        """Очистка всех компонентов"""
        if not self.components:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить все компоненты?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.components.clear()
            self.update_components_table()
            self.status_bar.showMessage("Все компоненты удалены")
            
    def check_barcode(self):
        """Проверка штрих-кода оператором"""
        barcode = self.barcode_input.text().strip()
        
        if len(barcode) != 27:
            self.show_result("❌ Ошибка", f"Неверная длина штрих-кода: {len(barcode)} символов (должно быть 27)")
            self.update_stats_table(barcode, "❌ Ошибка", f"Неверная длина: {len(barcode)} символов")
            return
            
        code = barcode[:10]
        batch = barcode[10:15]
        
        found = False
        found_component = None
        
        for component in self.components:
            if component['code'] == code and component['batch'] == batch:
                found = True
                found_component = component
                break
                
        if found:
            message = "✅ Ок компонент внесен верно"
            details = f"Код: {code}, Партия: {batch}, Количество на плату: {found_component['quantity']}"
            self.show_result("✅ УСПЕХ", message, details)
            self.update_stats_table(barcode, "✅ Успех", message)
            
            if found_component and not any(
                vc['code'] == code and vc['batch'] == batch 
                for vc in self.verified_components
            ):
                self.verified_components.append({
                    'code': code,
                    'batch': batch,
                    'quantity': found_component['quantity']
                })
                self.update_verified_table()
        else:
            message = f"❌ Компонент не найден. Код: {code}, Партия: {batch}"
            self.show_result("❌ ОШИБКА", message)
            self.update_stats_table(barcode, "❌ Ошибка", message)
            
        scan_record = {
            'id': len(self.scan_history) + 1,
            'barcode': barcode,
            'code': code,
            'batch': batch,
            'status': "SUCCESS" if found else "ERROR",
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.scan_history.append(scan_record)
        self.update_history_table()
        
        QTimer.singleShot(2000, lambda: self.barcode_input.clear() if self.barcode_input.text() == barcode else None)
        
    def show_result(self, title, message, details=""):
        """Отображение результата проверки"""
        self.result_frame.setVisible(True)
        self.result_label.setText(title)
        
        if details:
            self.details_label.setText(f"{message}\n{details}")
        else:
            self.details_label.setText(message)
            
        if "✅" in title or "УСПЕХ" in title:
            self.result_frame.setStyleSheet("background-color: #d5f4e6; border: 2px solid #2ecc71;")
        else:
            self.result_frame.setStyleSheet("background-color: #fadbd8; border: 2px solid #e74c3c;")
            
    def clear_scan(self):
        """Очистка поля сканирования"""
        self.barcode_input.clear()
        self.result_frame.setVisible(False)
        
    def clear_verified_components(self):
        """Очистка списка проверенных компонентов"""
        if not self.verified_components:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить список проверенных компонентов?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.verified_components.clear()
            self.update_verified_table()
            self.status_bar.showMessage("Список проверенных компонентов очищен")
            
    def update_verified_table(self):
        """Обновление таблицы проверенных компонентов"""
        self.verified_table.setRowCount(len(self.verified_components))
        
        for row, component in enumerate(self.verified_components):
            self.verified_table.setItem(row, 0, QTableWidgetItem(component['code']))
            self.verified_table.setItem(row, 1, QTableWidgetItem(component['batch']))
            self.verified_table.setItem(row, 2, QTableWidgetItem(str(component['quantity'])))
            
    def update_stats_table(self, barcode, status, message):
        """Обновление таблицы статистики"""
        row = self.stats_table.rowCount()
        self.stats_table.insertRow(row)
        
        self.stats_table.setItem(row, 0, QTableWidgetItem(barcode))
        self.stats_table.setItem(row, 1, QTableWidgetItem(status))
        self.stats_table.setItem(row, 2, QTableWidgetItem(message))
        
        time_str = datetime.now().strftime("%H:%M:%S")
        self.stats_table.setItem(row, 3, QTableWidgetItem(time_str))
        
        self.stats_table.scrollToBottom()
        
    def generate_qr_code(self):
        """Генерация случайного QR-кода"""
        chars = string.ascii_uppercase + string.digits
        return '@' + ''.join(random.choices(chars, k=5))
        
    def process_qr_code(self, qr_code):
        """Обработка сканирования QR-кода"""
        components_info = []
        for vc in self.verified_components:
            components_info.append({
                'code': vc['code'],
                'batch': vc['batch'],
                'quantity': vc['quantity']
            })
        
        result = {
            'qr_code': qr_code,
            'components': components_info,
            'program': self.current_program if self.current_program else 'Не выбрана',
            'date': datetime.now().strftime("%d.%m.%Y"),
            'time': datetime.now().strftime("%H:%M:%S"),
            'timestamp': datetime.now().isoformat()
        }
        
        self.qr_scan_history.append(result)
        
        display_text = f"""
Дата: {result['date']}
Время: {result['time']}
Программа: {result['program']}
QR-код: {qr_code}
Установленные компоненты:
"""
        if components_info:
            for i, comp in enumerate(components_info, 1):
                display_text += f"  {i}. Код: {comp['code']}, Партия: {comp['batch']}, Количество: {comp['quantity']}\n"
        else:
            display_text += "  Нет проверенных компонентов\n"

        display_text += "---\n"

        self.scan_display.append(display_text)
        self.add_qr_scan_to_history(result)

        self.verified_components.clear()
        self.update_verified_table()

        self.scan_counter += 1
        self.scan_counter_label.setText(f"Сканировано: {self.scan_counter}")
        
    def add_qr_scan_to_history(self, result):
        """Добавление записи в историю QR-сканирований"""
        row = self.qr_history_table.rowCount()
        self.qr_history_table.insertRow(row)

        self.qr_history_table.setItem(row, 0, QTableWidgetItem(result['date']))
        self.qr_history_table.setItem(row, 1, QTableWidgetItem(result['time']))
        self.qr_history_table.setItem(row, 2, QTableWidgetItem(result['program']))
        self.qr_history_table.setItem(row, 3, QTableWidgetItem(result['qr_code']))

        components_text = ""
        if result['components']:
            for comp in result['components']:
                components_text += f"{comp['code']}/{comp['batch']} (x{comp['quantity']}); "
        else:
            components_text = "Нет компонентов"
        self.qr_history_table.setItem(row, 4, QTableWidgetItem(components_text))

        details = f"QR-код: {result['qr_code']}, Программа: {result['program']}"
        self.qr_history_table.setItem(row, 5, QTableWidgetItem(details))

        self.qr_history_table.scrollToBottom()
        
    def start_qr_scanning(self):
        """Запуск автоматического сканирования QR-кодов"""
        if self.is_scanning or not self.qr_auto_radio.isChecked():
            return

        self.is_scanning = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.scan_status_label.setText("Статус: Сканирование...")
        self.scan_status_label.setStyleSheet("color: #2ecc71;")

        self.scan_counter = 0
        self.scan_counter_label.setText(f"Сканировано: {self.scan_counter}")

        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.scan_qr_cycle)
        self.scan_timer.start(2000)
        
    def scan_qr_cycle(self):
        """Цикл сканирования QR-кода (вызывается по таймеру)"""
        if not self.is_scanning:
            return

        qr_code = self.generate_qr_code()
        self.process_qr_code(qr_code)
        
    def stop_qr_scanning(self):
        """Остановка автоматического сканирования QR-кодов"""
        self.is_scanning = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.scan_status_label.setText("Статус: Остановлено")
        self.scan_status_label.setStyleSheet("color: #e74c3c;")

        if hasattr(self, 'scan_timer'):
            self.scan_timer.stop()
            
    def clear_qr_history(self):
        """Очистка истории QR-сканирований"""
        if not self.qr_scan_history:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить историю QR-сканирований?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.qr_scan_history.clear()
            self.qr_history_table.setRowCount(0)
            self.scan_display.clear()
            self.status_bar.showMessage("История QR-сканирований очищена")
            
    def export_qr_history(self):
        """Экспорт истории QR-сканирований"""
        if not self.qr_scan_history:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта!")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить историю QR-сканирований", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write("Дата;Время;Программа;QR-код;Компоненты\n")
                    
                    for record in self.qr_scan_history:
                        components_text = ""
                        if record['components']:
                            for comp in record['components']:
                                components_text += f"{comp['code']}/{comp['batch']}(x{comp['quantity']}); "
                        
                        f.write(f"{record['date']};{record['time']};{record['program']};{record['qr_code']};{components_text}\n")
                        
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
        
    def update_history_table(self):
        """Обновление таблицы истории"""
        self.history_table.setRowCount(len(self.scan_history))
        
        for row, record in enumerate(self.scan_history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(record['barcode']))
            
            status_item = QTableWidgetItem("✅ Успех" if record['status'] == "SUCCESS" else "❌ Ошибка")
            self.history_table.setItem(row, 2, status_item)
            
            self.history_table.setItem(row, 3, QTableWidgetItem(record['message']))
            
            try:
                dt = datetime.fromisoformat(record['timestamp'])
                time_str = dt.strftime("%d.%m.%Y %H:%M:%S")
            except:
                time_str = record['timestamp']
            self.history_table.setItem(row, 4, QTableWidgetItem(time_str))
            
    def filter_history(self):
        """Фильтрация истории"""
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        selected_status = self.status_filter.currentText()
        
        filtered_history = []
        
        for record in self.scan_history:
            record_date = record['timestamp'][:10]
            
            if selected_status == "Все":
                status_match = True
            elif selected_status == "Успешно":
                status_match = record['status'] == "SUCCESS"
            else:
                status_match = record['status'] == "ERROR"
                
            if (record_date == selected_date or self.date_filter.date() == QDate.currentDate()) and status_match:
                filtered_history.append(record)
                
        self.history_table.setRowCount(len(filtered_history))
        
        for row, record in enumerate(filtered_history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(record['barcode']))
            
            status_item = QTableWidgetItem("✅ Успех" if record['status'] == "SUCCESS" else "❌ Ошибка")
            self.history_table.setItem(row, 2, status_item)
            
            self.history_table.setItem(row, 3, QTableWidgetItem(record['message']))
            
            try:
                dt = datetime.fromisoformat(record['timestamp'])
                time_str = dt.strftime("%d.%m.%Y %H:%M:%S")
            except:
                time_str = record['timestamp']
            self.history_table.setItem(row, 4, QTableWidgetItem(time_str))
            
    def export_history(self):
        """Экспорт истории в CSV"""
        if not self.scan_history:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта!")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить историю", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write("ID;Штрих-код;Код;Партия;Статус;Сообщение;Время\n")
                    
                    for record in self.scan_history:
                        f.write(f"{record['id']};{record['barcode']};{record['code']};{record['batch']};")
                        f.write(f"{record['status']};{record['message']};{record['timestamp']}\n")
                        
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
                
    def clear_history(self):
        """Очистка истории"""
        if not self.scan_history:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить всю историю?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.scan_history.clear()
            self.update_history_table()
            self.stats_table.setRowCount(0)
            self.status_bar.showMessage("История очищена")
            
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.save_data()
        
        if self.scan_history:
            history_file = f"{self.results_dir}/scan_history_{datetime.now().strftime('%Y%m%d')}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.scan_history, f, ensure_ascii=False, indent=2)
                
        if self.qr_scan_history:
            qr_history_file = f"{self.qr_results_dir}/qr_history_{datetime.now().strftime('%Y%m%d')}.json"
            with open(qr_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.qr_scan_history, f, ensure_ascii=False, indent=2)
                
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ComponentTrackerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
