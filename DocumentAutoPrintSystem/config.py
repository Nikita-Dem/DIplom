# Конфигурационные параметры приложения

class Config:
    # Настройки базы данных
    DATABASE_PATH = 'database/documents.db'

    # Настройки путей
    OUTPUT_DIR = 'output'
    TEMPLATES_DIR = 'templates'

    # Настройки документов
    DEFAULT_AUTHOR = 'Система'
    DEFAULT_STATUS = 'draft'

    # Настройки интерфейса
    APP_TITLE = 'Система формирования и печати документов'
    APP_SIZE = (1200, 700)

    # Настройки печати
    DEFAULT_PRINTER = 'default'

    @classmethod
    def get_database_url(cls):
        """Получение URL базы данных"""
        return f'sqlite:///{cls.DATABASE_PATH}'

    @classmethod
    def get_output_path(cls, doc_type):
        """Получение пути для выходных файлов"""
        import os
        path = os.path.join(cls.OUTPUT_DIR, doc_type)
        os.makedirs(path, exist_ok=True)
        return path