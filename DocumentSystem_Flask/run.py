#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска Flask-приложения с автоматическим созданием папок
"""

import os
import sys
import subprocess


def setup_environment():
    """Настройка окружения перед запуском"""
    print("=" * 60)
    print("🚀 ПОДГОТОВКА СИСТЕМЫ ДОКУМЕНТООБОРОТА")
    print("=" * 60)

    # Создаем необходимые папки
    directories = [
        'instance',
        'output',
        'output/protocols',
        'output/resolutions',
        'templates',
        'static/css',
        'static/js'
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Папка создана: {directory}")
        except Exception as e:
            print(f"✗ Ошибка при создании папки {directory}: {e}")

    # Проверяем наличие файла .env
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('SECRET_KEY=your-super-secret-key-change-this-in-production\n')
        print("✓ Создан файл .env с секретным ключом")

    # Проверяем права на запись в папку instance
    test_file = os.path.join('instance', 'test.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✓ Права на запись в папку instance есть")
    except Exception as e:
        print(f"✗ Ошибка прав доступа к папке instance: {e}")
        return False

    print("\n✅ Окружение готово к запуску")
    return True


if __name__ == "__main__":
    if setup_environment():
        print("\n🚀 Запуск приложения...\n")
        # Запускаем app.py
        subprocess.run([sys.executable, 'app.py'])
    else:
        print("\n❌ Ошибка при подготовке окружения")
        input("Нажмите Enter для выхода...")