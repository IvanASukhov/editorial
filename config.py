import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Секретный ключ для сессий и форм Flask-WTF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'top-secret-key-12345'
    # Путь к базе данных SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Ограничение на размер загружаемых файлов (10 МБ)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    # Папка для загрузки файлов (рукописи, рецензии)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'media')
    # Разрешённые расширения файлов для загрузки
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'rtf', 'txt'}
    # Flask-WTF config
    WTF_CSRF_ENABLED = False

# Для совместимости
config = Config
