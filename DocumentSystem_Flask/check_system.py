#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для диагностики системы перед запуском
"""

import os
import sys
import sqlite3
from pathlib import Path


def check_python():
    """Проверка версии Python"""
    print(f"🐍 Python версия: {sys.version}")
    print(f"📁 Путь к Python: {sys.executable}")
    return True


def check_directories():
    """Проверка наличия и прав доступа к папкам"""
    print("\n📁 Проверка папок:")

    directories = [
        'instance',
        'output',
        'output/protocols',
        'output/resolutions',
        'templates',
        'static',
        'static/css',
        'static/js'
    ]

    all_ok = True
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Создана папка: {directory}")
            except Exception as e:
                print(f"  ✗ Не удалось создать папку {directory}: {e}")
                all_ok = False
        else:
            # Проверяем права на запись
            test_file = path / 'test.tmp'
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                test_file.unlink()
                print(f"  ✓ Папка существует и доступна: {directory}")
            except Exception as e:
                print(f"  ✗ Нет прав на запись в папку {directory}: {e}")
                all_ok = False

    return all_ok


def check_database():
    """Проверка возможности создания базы данных"""
    print("\n💾 Проверка базы данных:")

    db_path = Path('instance') / 'documents.db'

    try:
        # Пробуем создать подключение к SQLite
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Пробуем создать тестовую таблицу
        cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)')
        cursor.execute('DROP TABLE test')

        conn.close()
        print(f"  ✓ База данных может быть создана по пути: {db_path}")

        # Удаляем тестовый файл если он создался
        if db_path.exists():
            db_path.unlink()

        return True
    except Exception as e:
        print(f"  ✗ Ошибка при работе с базой данных: {e}")
        return False


def check_imports():
    """Проверка импорта необходимых библиотек"""
    print("\n📦 Проверка библиотек:")

    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_wtf',
        'wtforms',
        'reportlab',
        'docx',
        'dotenv'
    ]

    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} установлен")
        except ImportError as e:
            print(f"  ✗ {package} НЕ УСТАНОВЛЕН: {e}")
            all_ok = False

    return all_ok


def main():
    """Главная функция диагностики"""
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА СИСТЕМЫ ДОКУМЕНТООБОРОТА")
    print("=" * 60)

    checks = [
        check_python(),
        check_directories(),
        check_database(),
        check_imports()
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("   Можно запускать приложение командой: python app.py")
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("   Исправьте ошибки перед запуском")
    print("=" * 60)

    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()