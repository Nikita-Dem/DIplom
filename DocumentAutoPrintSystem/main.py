import sys
from gui import run_app
from database import db_manager
    

def main():
    """Главная функция приложения"""
    print("=" * 60)
    print("СИСТЕМА АВТОМАТИЧЕСКОГО ФОРМИРОВАНИЯ И ПЕЧАТИ ДОКУМЕНТОВ")
    print("=" * 60)

    # Проверка и инициализация базы данных
    print("Инициализация системы...")

    # Запуск графического интерфейса
    run_app()


if __name__ == "__main__":
    main()