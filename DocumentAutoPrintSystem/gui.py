from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QPushButton, QLabel,
                             QLineEdit, QTextEdit, QDateEdit, QListWidget,
                             QListWidgetItem, QMessageBox, QFileDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout,
                             QComboBox, QSpinBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from datetime import datetime
import sys
from database import db_manager
from document_generator import DocumentGenerator


class DocumentApp(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.document_generator = DocumentGenerator()
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Система формирования и печати документов')
        self.setGeometry(100, 100, 1200, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Вкладки
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Вкладка 1: Создание протокола
        self.create_protocol_tab(tab_widget)

        # Вкладка 2: Создание постановления
        self.create_resolution_tab(tab_widget)

        # Вкладка 3: Просмотр документов
        self.create_documents_tab(tab_widget)

        # Кнопки управления
        button_layout = QHBoxLayout()

        print_btn = QPushButton('Печать')
        print_btn.clicked.connect(self.print_document)
        button_layout.addWidget(print_btn)

        export_btn = QPushButton('Экспорт')
        export_btn.clicked.connect(self.export_document)
        button_layout.addWidget(export_btn)

        refresh_btn = QPushButton('Обновить список')
        refresh_btn.clicked.connect(self.refresh_documents)
        button_layout.addWidget(refresh_btn)

        main_layout.addLayout(button_layout)

    def create_protocol_tab(self, tab_widget):
        """Создание вкладки для протоколов"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Форма ввода данных
        form_group = QGroupBox("Данные протокола")
        form_layout = QFormLayout()

        self.protocol_number = QSpinBox()
        self.protocol_number.setMinimum(1)
        self.protocol_number.setMaximum(9999)

        self.protocol_date = QDateEdit()
        self.protocol_date.setDate(QDate.currentDate())
        self.protocol_date.setCalendarPopup(True)

        self.protocol_topic = QLineEdit()
        self.protocol_location = QLineEdit()
        self.protocol_datetime = QLineEdit()

        self.protocol_participants = QTextEdit()
        self.protocol_participants.setMaximumHeight(100)

        self.protocol_agenda = QTextEdit()
        self.protocol_agenda.setMaximumHeight(100)

        self.protocol_decisions = QTextEdit()
        self.protocol_decisions.setMaximumHeight(100)

        self.protocol_chairman = QLineEdit()
        self.protocol_secretary = QLineEdit()

        form_layout.addRow("Номер протокола:", self.protocol_number)
        form_layout.addRow("Дата:", self.protocol_date)
        form_layout.addRow("Тема:", self.protocol_topic)
        form_layout.addRow("Место проведения:", self.protocol_location)
        form_layout.addRow("Дата и время заседания:", self.protocol_datetime)
        form_layout.addRow("Участники (каждый с новой строки):", self.protocol_participants)
        form_layout.addRow("Повестка дня (каждый пункт с новой строки):", self.protocol_agenda)
        form_layout.addRow("Решения (каждое с новой строки):", self.protocol_decisions)
        form_layout.addRow("Председатель:", self.protocol_chairman)
        form_layout.addRow("Секретарь:", self.protocol_secretary)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопка создания
        create_btn = QPushButton('Создать протокол (PDF)')
        create_btn.clicked.connect(self.create_protocol)
        layout.addWidget(create_btn)

        tab_widget.addTab(widget, "Протокол")

    def create_resolution_tab(self, tab_widget):
        """Создание вкладки для постановлений"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Форма ввода данных
        form_group = QGroupBox("Данные постановления")
        form_layout = QFormLayout()

        self.resolution_number = QSpinBox()
        self.resolution_number.setMinimum(1)
        self.resolution_number.setMaximum(9999)

        self.resolution_date = QDateEdit()
        self.resolution_date.setDate(QDate.currentDate())
        self.resolution_date.setCalendarPopup(True)

        self.resolution_topic = QLineEdit()
        self.resolution_basis = QTextEdit()
        self.resolution_basis.setMaximumHeight(80)

        self.resolution_text = QTextEdit()
        self.resolution_text.setMaximumHeight(150)

        self.resolution_chairman = QLineEdit()

        self.resolution_members = QTextEdit()
        self.resolution_members.setMaximumHeight(80)

        form_layout.addRow("Номер постановления:", self.resolution_number)
        form_layout.addRow("Дата:", self.resolution_date)
        form_layout.addRow("Тема:", self.resolution_topic)
        form_layout.addRow("Основание:", self.resolution_basis)
        form_layout.addRow("Текст постановления (каждый пункт с новой строки):", self.resolution_text)
        form_layout.addRow("Председатель:", self.resolution_chairman)
        form_layout.addRow("Члены комиссии (каждый с новой строки):", self.resolution_members)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопка создания
        create_btn = QPushButton('Создать постановление (DOCX)')
        create_btn.clicked.connect(self.create_resolution)
        layout.addWidget(create_btn)

        tab_widget.addTab(widget, "Постановление")

    def create_documents_tab(self, tab_widget):
        """Создание вкладки для просмотра документов"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Фильтры
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Тип документа:")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все документы")
        self.filter_combo.addItem("Протоколы")
        self.filter_combo.addItem("Постановления")
        self.filter_combo.currentTextChanged.connect(self.load_documents)
        filter_layout.addWidget(self.filter_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица документов
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(7)
        self.documents_table.setHorizontalHeaderLabels([
            "ID", "Тип", "Номер", "Дата", "Название", "Автор", "Статус"
        ])

        # Настройка таблицы
        header = self.documents_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        layout.addWidget(self.documents_table)

        # Кнопки управления документами
        button_layout = QHBoxLayout()

        view_btn = QPushButton('Просмотреть')
        view_btn.clicked.connect(self.view_document)
        button_layout.addWidget(view_btn)

        delete_btn = QPushButton('Удалить')
        delete_btn.clicked.connect(self.delete_document)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        tab_widget.addTab(widget, "Все документы")

        # Загружаем документы при открытии
        self.load_documents()

    def create_protocol(self):
        """Создание протокола"""
        try:
            # Собираем данные
            data = {
                'number': str(self.protocol_number.value()),
                'date': self.protocol_date.date().toString('dd.MM.yyyy'),
                'topic': self.protocol_topic.text(),
                'location': self.protocol_location.text(),
                'datetime': self.protocol_datetime.text(),
                'participants': self.protocol_participants.toPlainText().split('\n'),
                'agenda': self.protocol_agenda.toPlainText().split('\n'),
                'decisions': self.protocol_decisions.toPlainText().split('\n'),
                'chairman': self.protocol_chairman.text(),
                'secretary': self.protocol_secretary.text(),
                'author': 'Пользователь'
            }

            # Генерируем документ
            filepath, doc_id = self.document_generator.generate_protocol(data)

            QMessageBox.information(
                self,
                'Успех',
                f'Протокол создан!\nФайл: {filepath}\nID в базе: {doc_id}'
            )

            # Обновляем список документов
            self.load_documents()

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось создать протокол: {str(e)}')

    def create_resolution(self):
        """Создание постановления"""
        try:
            # Собираем данные
            data = {
                'number': str(self.resolution_number.value()),
                'date': self.resolution_date.date().toString('dd.MM.yyyy'),
                'topic': self.resolution_topic.text(),
                'basis': self.resolution_basis.toPlainText(),
                'resolutions': self.resolution_text.toPlainText().split('\n'),
                'chairman': self.resolution_chairman.text(),
                'members': self.resolution_members.toPlainText().split('\n'),
                'author': 'Пользователь'
            }

            # Генерируем документ
            filepath, doc_id = self.document_generator.generate_resolution(data)

            QMessageBox.information(
                self,
                'Успех',
                f'Постановление создано!\nФайл: {filepath}\nID в базе: {doc_id}'
            )

            # Обновляем список документов
            self.load_documents()

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось создать постановление: {str(e)}')

    def load_documents(self):
        """Загрузка документов в таблицу"""
        try:
            filter_text = self.filter_combo.currentText()
            document_type = None

            if filter_text == "Протоколы":
                document_type = 'protocol'
            elif filter_text == "Постановления":
                document_type = 'resolution'

            documents = db_manager.get_all_documents(document_type)

            self.documents_table.setRowCount(len(documents))

            for row, doc in enumerate(documents):
                self.documents_table.setItem(row, 0, QTableWidgetItem(str(doc.id)))
                self.documents_table.setItem(row, 1, QTableWidgetItem(
                    'Протокол' if doc.document_type == 'protocol' else 'Постановление'
                ))
                self.documents_table.setItem(row, 2, QTableWidgetItem(str(doc.document_number)))
                self.documents_table.setItem(row, 3, QTableWidgetItem(
                    doc.document_date.strftime('%d.%m.%Y') if doc.document_date else ''
                ))
                self.documents_table.setItem(row, 4, QTableWidgetItem(doc.title))
                self.documents_table.setItem(row, 5, QTableWidgetItem(doc.author))
                self.documents_table.setItem(row, 6, QTableWidgetItem(doc.status))

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить документы: {str(e)}')

    def view_document(self):
        """Просмотр выбранного документа"""
        selected_items = self.documents_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите документ для просмотрения')
            return

        row = selected_items[0].row()
        doc_id = int(self.documents_table.item(row, 0).text())

        document = db_manager.get_document(doc_id)
        if document and document.file_path:
            try:
                import os
                import subprocess

                # Открываем файл в ассоциированной программе
                if os.name == 'nt':
                    os.startfile(document.file_path)
                elif os.name == 'posix':
                    subprocess.call(['xdg-open', document.file_path])
                else:
                    QMessageBox.information(
                        self,
                        'Информация',
                        f'Файл: {document.file_path}\nОткройте файл вручную.'
                    )
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось открыть файл: {str(e)}')

    def delete_document(self):
        """Удаление выбранного документа"""
        selected_items = self.documents_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите документ для удаления')
            return

        row = selected_items[0].row()
        doc_id = int(self.documents_table.item(row, 0).text())

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить этот документ?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db_manager.delete_document(doc_id):
                QMessageBox.information(self, 'Успех', 'Документ удален')
                self.load_documents()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось удалить документ')

    def print_document(self):
        """Печать выбранного документа"""
        selected_items = self.documents_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите документ для печати')
            return

        row = selected_items[0].row()
        doc_id = int(self.documents_table.item(row, 0).text())

        document = db_manager.get_document(doc_id)
        if document and document.file_path:
            if self.document_generator.print_document(document.file_path):
                QMessageBox.information(self, 'Успех', 'Документ отправлен на печать')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось отправить документ на печать')

    def export_document(self):
        """Экспорт документа"""
        selected_items = self.documents_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите документ для экспорта')
            return

        row = selected_items[0].row()
        doc_id = int(self.documents_table.item(row, 0).text())

        document = db_manager.get_document(doc_id)
        if document and document.file_path:
            try:
                # Диалог выбора папки
                folder = QFileDialog.getExistingDirectory(self, "Выберите папку для экспорта")
                if folder:
                    import shutil
                    import os

                    filename = os.path.basename(document.file_path)
                    destination = os.path.join(folder, filename)

                    shutil.copy2(document.file_path, destination)
                    QMessageBox.information(self, 'Успех', f'Документ экспортирован в: {destination}')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось экспортировать документ: {str(e)}')

    def refresh_documents(self):
        """Обновление списка документов"""
        self.load_documents()
        QMessageBox.information(self, 'Обновлено', 'Список документов обновлен')


def run_app():
    """Запуск приложения"""
    app = QApplication(sys.argv)
    window = DocumentApp()
    window.show()
    sys.exit(app.exec_())