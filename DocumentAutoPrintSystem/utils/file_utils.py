import os
import shutil
from datetime import datetime


class FileUtils:
    """Утилиты для работы с файлами"""

    @staticmethod
    def ensure_directory(path):
        """Создание директории, если её нет"""
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def generate_filename(prefix, extension, with_timestamp=True):
        """Генерация имени файла"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if with_timestamp else ''
        filename = f"{prefix}_{timestamp}.{extension}".strip('_')
        return filename

    @staticmethod
    def get_file_size(filepath):
        """Получение размера файла"""
        try:
            return os.path.getsize(filepath)
        except:
            return 0

    @staticmethod
    def backup_file(filepath):
        """Создание резервной копии файла"""
        if os.path.exists(filepath):
            backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d')}"
            shutil.copy2(filepath, backup_path)
            return backup_path
        return None