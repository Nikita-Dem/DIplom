import os
import sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def check_fonts():
    """Проверка наличия шрифтов с поддержкой кириллицы"""

    print("=" * 60)
    print("🔍 ПРОВЕРКА ШРИФТОВ ДЛЯ PDF")
    print("=" * 60)

    # Проверяем папку fonts
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    if os.path.exists(fonts_dir):
        print(f"\n📁 Папка fonts найдена: {fonts_dir}")
        files = os.listdir(fonts_dir)
        ttf_files = [f for f in files if f.endswith('.ttf')]

        if ttf_files:
            print(f"✅ Найдены TTF шрифты:")
            for f in ttf_files:
                print(f"   - {f}")
        else:
            print("❌ В папке fonts нет TTF файлов")
    else:
        print(f"\n❌ Папка fonts не найдена по пути: {fonts_dir}")
        print("   Создайте папку 'fonts' и поместите туда DejaVuSans.ttf")

    # Проверяем системные шрифты
    print("\n💻 Проверка системных шрифтов:")

    if sys.platform == 'win32':
        windows_dir = os.environ.get('WINDIR', 'C:\\Windows')
        font_dir = os.path.join(windows_dir, 'Fonts')

        candidates = ['arial.ttf', 'times.ttf', 'calibri.ttf', 'segoeui.ttf']

        for candidate in candidates:
            path = os.path.join(font_dir, candidate)
            if os.path.exists(path):
                print(f"✅ Найден: {path}")
            else:
                print(f"❌ Не найден: {candidate}")

    print("\n" + "=" * 60)
    print("Рекомендация: скачайте DejaVu Sans шрифты")
    print("и поместите их в папку 'fonts' вашего проекта")
    print("=" * 60)


if __name__ == "__main__":
    check_fonts()