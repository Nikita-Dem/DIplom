import os
import requests
import zipfile
import shutil


def download_dejavu_fonts():
    """Скачивание и установка шрифтов DejaVu с поддержкой кириллицы"""

    # Создаем папку fonts
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)

    # URL для скачивания шрифтов DejaVu
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    url_bold = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf"

    try:
        # Скачиваем обычный шрифт
        print("Скачивание DejaVuSans.ttf...")
        response = requests.get(url)
        with open(os.path.join(fonts_dir, 'DejaVuSans.ttf'), 'wb') as f:
            f.write(response.content)

        # Скачиваем жирный шрифт
        print("Скачивание DejaVuSans-Bold.ttf...")
        response = requests.get(url_bold)
        with open(os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf'), 'wb') as f:
            f.write(response.content)

        print("✅ Шрифты успешно скачаны в папку 'fonts'")
        return True

    except Exception as e:
        print(f"❌ Ошибка при скачивании шрифтов: {e}")
        return False


if __name__ == "__main__":
    download_dejavu_fonts()