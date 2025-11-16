from models import db, User, Manuscript, Review, Publication, News, Message, ManuscriptHistory
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import os


def init_db(app=None):
    """
    Инициализация БД: создание и первичное наполнение.
    Вызывается из app.py при первом запуске, если БД ещё не существует.
    """
    if app is not None:
        # ВНИМАНИЕ: здесь НЕ надо вызывать db.init_app(app) — он уже вызван в app.py
        with app.app_context():
            _init_and_fill()
    else:
        # для запуска из отдельного скрипта (если нужно)
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            _init_and_fill()


def _init_and_fill():
    # Создать таблицы
    db.create_all()

    # Проверка, если БД уже наполнена — не дублировать
    if User.query.first():
        print("Database already initialized. Skipping test data insert.")
        return

    # === Пользователи ===
    admin = User(
        full_name="Администратор Сайта",
        email="admin@editorial.ru",
        password_hash=generate_password_hash("adminpass"),
        role="admin"
    )
    staff = User(
        full_name="Редактор Иванов И.И.",
        email="editor@editorial.ru",
        password_hash=generate_password_hash("editorpass"),
        role="staff"
    )
    reviewer = User(
        full_name="Рецензент Петров П.П.",
        email="reviewer@editorial.ru",
        password_hash=generate_password_hash("reviewpass"),
        role="reviewer"
    )
    author = User(
        full_name="Автор Сидоров А.А.",
        email="author@editorial.ru",
        password_hash=generate_password_hash("authorpass"),
        role="author"
    )
    db.session.add_all([admin, staff, reviewer, author])
    db.session.commit()

    # === Публикации ===
    pub1 = Publication(
        type="journal",
        title="Научный журнал МУИВ",
        pub_date=date(2024, 5, 15),
        description="Выпуск №1 за 2024 год"
    )
    pub2 = Publication(
        type="book",
        title="Сборник научных статей",
        pub_date=date(2024, 6, 1),
        description="Лучшие статьи студентов"
    )
    db.session.add_all([pub1, pub2])
    db.session.commit()

    # === Новости ===
    news1 = News(
        title="Открыта подача рукописей",
        content="Уважаемые авторы! Открыта подача рукописей на следующий выпуск.",
        published_at=datetime(2024, 4, 10)
    )
    news2 = News(
        title="Итоги предыдущего выпуска",
        content="Вышел новый номер журнала. Ознакомьтесь с публикациями на сайте.",
        published_at=datetime(2024, 5, 20)
    )
    db.session.add_all([news1, news2])
    db.session.commit()

    # убедимся, что каталог для рукописей существует
    os.makedirs("media/manuscripts", exist_ok=True)

    # === Рукописи ===
    m1 = Manuscript(
        title="Инновационные методы преподавания",
        description="Актуальные подходы к обучению в цифровую эпоху.",
        file_path="media/manuscripts/primer_rukopisi1.pdf",
        status="submitted",
        author_id=author.id,
        publication_id=pub1.id
    )
    m2 = Manuscript(
        title="Проблемы автоматизации издательских процессов",
        description="Обзор современных платформ для издательств.",
        file_path="media/manuscripts/primer_rukopisi2.docx",
        status="under_review",
        author_id=author.id,
        publication_id=pub2.id
    )
    db.session.add_all([m1, m2])
    db.session.commit()

    # === Рецензии ===
    r1 = Review(
        manuscript_id=m2.id,
        reviewer_id=reviewer.id,
        text="Статья интересная, но требует доработки по разделу 2.",
        score=4,
        status="submitted"
    )
    db.session.add(r1)
    db.session.commit()

    # === История рукописей (комментарии / статусы) ===
    h1 = ManuscriptHistory(
        manuscript_id=m1.id,
        actor_id=author.id,
        actor_role="author",
        action="submitted",
        comment="Автор отправил рукопись в редакцию."
    )
    h2 = ManuscriptHistory(
        manuscript_id=m2.id,
        actor_id=author.id,
        actor_role="author",
        action="submitted",
        comment="Автор загрузил рукопись для рассмотрения."
    )
    h3 = ManuscriptHistory(
        manuscript_id=m2.id,
        actor_id=reviewer.id,
        actor_role="reviewer",
        action="review_submitted",
        comment="Рецензент оставил замечания и рекомендацию доработать текст."
    )
    db.session.add_all([h1, h2, h3])
    db.session.commit()

    # === Сообщения (обратная связь) ===
    msg1 = Message(
        sender_id=author.id,
        sender_email=None,
        subject="Вопрос по срокам публикации",
        body="Когда будет опубликована моя рукопись?",
        sent_at=datetime.now(),
        status="new"
    )
    msg2 = Message(
        sender_id=staff.id,
        sender_email=None,
        subject="Ответ на ваш вопрос",
        body="Ориентировочная дата публикации — июнь 2024 года.",
        sent_at=datetime.now(),
        status="done"
    )
    msg3 = Message(
        sender_id=None,
        sender_email="external_author@example.com",
        subject="Запрос информации",
        body="Хотел бы уточнить требования к оформлению рукописи.",
        sent_at=datetime.now(),
        status="new"
    )
    db.session.add_all([msg1, msg2, msg3])
    db.session.commit()

    print("Database created and filled with demo data.")


# Точка входа для ручного запуска (опционально)
if __name__ == "__main__":
    init_db()
