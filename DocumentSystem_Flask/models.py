from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

db = SQLAlchemy()

class Document(db.Model):
    """Модель для хранения документов"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False)  # 'protocol' или 'resolution'
    document_number = db.Column(db.String(50), nullable=False)
    document_date = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)  # JSON с данными документа (опционально)
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now)
    author = db.Column(db.String(100), default='Пользователь')
    status = db.Column(db.String(50), default='final')

    def to_dict(self):
        """Преобразование в словарь для шаблонов"""
        # Обработка document_date
        doc_date = self.document_date
        if isinstance(doc_date, str):
            try:
                doc_date = datetime.strptime(doc_date, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    doc_date = datetime.strptime(doc_date, '%Y-%m-%d %H:%M:%S')
                except:
                    doc_date = datetime.now()
        elif doc_date is None:
            doc_date = datetime.now()

        # Обработка created_at
        created = self.created_at
        if isinstance(created, str):
            try:
                created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                except:
                    created = datetime.now()
        elif created is None:
            created = datetime.now()

        # Безопасное получение имени файла
        file_name = ''
        if self.file_path and isinstance(self.file_path, str):
            try:
                file_name = os.path.basename(self.file_path)
            except:
                file_name = ''

        return {
            'id': self.id,
            'document_type': 'Протокол' if self.document_type == 'protocol' else 'Постановление',
            'document_type_code': self.document_type,
            'document_number': self.document_number,
            'document_date': doc_date.strftime('%d.%m.%Y') if doc_date else '',
            'document_date_full': doc_date.strftime('%d.%m.%Y %H:%M') if doc_date else '',
            'title': self.title,
            'file_path': self.file_path,
            'file_name': file_name,
            'created_at': created.strftime('%d.%m.%Y %H:%M'),
            'author': self.author,
            'status': self.status
        }

    def __repr__(self):
        return f'<Document {self.document_type} #{self.document_number}>'