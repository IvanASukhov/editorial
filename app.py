from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os

from config import Config
from models import db
from db_init import init_db
from routes import routes

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)

    # Инициализация CSRF защиты для Flask-WTF
    csrf = CSRFProtect(app)

    # Инициализация базы данных
    db.init_app(app)

    # Автоматическое создание и наполнение базы при первом запуске
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        with app.app_context():
            init_db(app)

    # Регистрация всех маршрутов (routes.py)
    app.register_blueprint(routes)

    # Создание папок для загрузки файлов (если ещё нет)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    for subfolder in ['manuscripts', 'reviews', 'uploads']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], subfolder), exist_ok=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
