import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Базовая конфигурация
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-12345'

    # База данных - создаем папку instance если её нет
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')

    # Создаем папку instance, если её нет
    os.makedirs(instance_path, exist_ok=True)

    # Путь к файлу базы данных
    db_path = os.path.join(instance_path, 'documents.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Пути для сохранения файлов
    OUTPUT_DIR = os.path.join(basedir, 'output')
    PROTOCOLS_DIR = os.path.join(OUTPUT_DIR, 'protocols')
    RESOLUTIONS_DIR = os.path.join(OUTPUT_DIR, 'resolutions')

    # Создаем папки для выходных файлов
    os.makedirs(PROTOCOLS_DIR, exist_ok=True)
    os.makedirs(RESOLUTIONS_DIR, exist_ok=True)

    # Максимальный размер загружаемого файла (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Настройки приложения
    DOCUMENTS_PER_PAGE = 10