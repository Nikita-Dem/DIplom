import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Document(Base):
    """Модель для хранения документов в базе данных"""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    document_type = Column(String(50))  # 'protocol' или 'resolution'
    document_number = Column(String(50))
    document_date = Column(DateTime)
    title = Column(String(255))
    content = Column(Text)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    author = Column(String(100))
    status = Column(String(50), default='draft')

    def __repr__(self):
        return f"<Document({self.document_type} #{self.document_number})>"


class DatabaseManager:
    """Менеджер для работы с базой данных"""

    def __init__(self, db_path='database/documents.db'):
        self.db_path = db_path
        self.engine = None
        self.Session = None
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        # Создаем папку для базы данных, если её нет
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Создаем соединение с базой данных
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)

        # Создаем фабрику сессий
        self.Session = sessionmaker(bind=self.engine)

        print(f"База данных инициализирована: {self.db_path}")

    def add_document(self, **kwargs):
        """Добавление нового документа в базу данных"""
        session = self.Session()
        try:
            document = Document(**kwargs)
            session.add(document)
            session.commit()
            print(f"Документ добавлен: {document}")
            return document.id
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении документа: {e}")
            return None
        finally:
            session.close()

    def get_document(self, document_id):
        """Получение документа по ID"""
        session = self.Session()
        document = session.query(Document).filter_by(id=document_id).first()
        session.close()
        return document

    def get_all_documents(self, document_type=None):
        """Получение всех документов (с возможностью фильтрации по типу)"""
        session = self.Session()
        query = session.query(Document)

        if document_type:
            query = query.filter_by(document_type=document_type)

        documents = query.order_by(Document.created_at.desc()).all()
        session.close()
        return documents

    def update_document(self, document_id, **kwargs):
        """Обновление документа"""
        session = self.Session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                for key, value in kwargs.items():
                    setattr(document, key, value)
                session.commit()
                print(f"Документ обновлен: {document}")
                return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении документа: {e}")
            return False
        finally:
            session.close()

    def delete_document(self, document_id):
        """Удаление документа"""
        session = self.Session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                session.delete(document)
                session.commit()
                print(f"Документ удален: {document}")
                return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка при удалении документа: {e}")
            return False
        finally:
            session.close()


# Создаем глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()