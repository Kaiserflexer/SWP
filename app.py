import os
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Путь к папке по умолчанию (media в каталоге приложения)
default_media_folder = os.path.join(os.getcwd(), 'media')

# Переменные для счетчика
total_downloaded = 0
total_failed = 0

# Определите маршрут для отображения главной страницы
@app.route("/")
def index():
    return render_template("index.html", total_downloaded=total_downloaded, total_failed=total_failed)

# Определите маршрут для скачивания медиа
@app.route("/download", methods=["POST"])
def download_media():
    global total_downloaded, total_failed
    total_downloaded = 0
    total_failed = 0

    url = request.form.get("url")
    media_folder = request.form.get("media_folder")

    if not media_folder:
        media_folder = default_media_folder

    if not os.path.exists(media_folder):
        os.makedirs(media_folder)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            media_elements = soup.find_all(['img', 'video', 'audio'])

            for element in media_elements:
                if 'src' in element.attrs:
                    media_url = element['src']
                    download_media_file(media_url, media_folder)

            result_message = "Файлы успешно скачаны"
        else:
            result_message = "Ошибка при обработке URL"
    except Exception as e:
        result_message = f"Ошибка при обработке URL: {e}"

    return jsonify({"total_downloaded": total_downloaded, "total_failed": total_failed, "result_message": result_message})

# Функция для скачивания медиа-файлов
def download_media_file(url, folder_path):
    global total_downloaded, total_failed

    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            if 'image' in content_type:
                file_extension = 'jpg'
            elif 'video' in content_type:
                file_extension = 'mp4'
            elif 'audio' in content_type:
                file_extension = 'mp3'
            else:
                return

            file_name = os.path.join(folder_path, f'{os.path.basename(url)}.{file_extension}')
            with open(file_name, 'wb') as file:
                file.write(response.content)

            total_downloaded += 1
        else:
            total_failed += 1
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        total_failed += 1

if __name__ == "__main__":
    app.run(debug=True)
