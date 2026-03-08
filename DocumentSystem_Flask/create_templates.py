#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def create_file(path, content):
    """Создание файла с содержимым"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Создан файл: {path}")


def main():
    """Создание всех шаблонов"""
    print("=" * 60)
    print("📁 СОЗДАНИЕ ШАБЛОНОВ ДЛЯ FLASK-ПРИЛОЖЕНИЯ")
    print("=" * 60)

    # Создаем папку templates
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    print(f"✓ Папка создана: {templates_dir}/")

    # Создаем папки для статических файлов
    static_dirs = ['static/css', 'static/js']
    for dir_path in static_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Папка создана: {dir_path}/")

    # Содержимое файлов (здесь нужно вставить содержимое каждого файла из инструкции выше)
    files = {
        'templates/base.html': '',  # Вставьте содержимое base.html
        'templates/index.html': '',  # Вставьте содержимое index.html
        'templates/create_protocol.html': '',  # Вставьте содержимое create_protocol.html
        'templates/create_resolution.html': '',  # Вставьте содержимое create_resolution.html
        'templates/documents_list.html': '',  # Вставьте содержимое documents_list.html
        'templates/view_document.html': '',  # Вставьте содержимое view_document.html
        'templates/404.html': '',  # Вставьте содержимое 404.html
        'templates/500.html': '',  # Вставьте содержимое 500.html
        'static/css/style.css': '',  # Вставьте содержимое style.css
    }

    # Создаем каждый файл
    for file_path, content in files.items():
        create_file(file_path, content)

    print("\n" + "=" * 60)
    print("✅ ВСЕ ШАБЛОНЫ УСПЕШНО СОЗДАНЫ!")
    print("=" * 60)
    print("\n📦 Созданы файлы:")
    for file_path in files.keys():
        print(f"   - {file_path}")

    print("\n🚀 Теперь можно запустить приложение командой:")
    print("   python app.py")


if __name__ == "__main__":
    main()