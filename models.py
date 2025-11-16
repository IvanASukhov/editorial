from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Пользователь: автор, редактор (staff), рецензент, администратор
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # author, staff, reviewer, admin
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_blocked = db.Column(db.Boolean, default=False)

    # связи
    manuscripts = db.relationship('Manuscript', backref='author', lazy=True)
    reviews_made = db.relationship('Review', foreign_keys='Review.reviewer_id',
                                   backref='reviewer_user', lazy=True)
    messages_sent = db.relationship('Message', backref='sender', lazy=True)
    history_entries = db.relationship('ManuscriptHistory',
                                      backref='actor',
                                      lazy=True,
                                      foreign_keys='ManuscriptHistory.actor_id')


class Manuscript(db.Model):
    __tablename__ = 'manuscripts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(32), nullable=False, default='submitted')
    # submitted, under_review, accepted, rejected, published

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'), nullable=True)

    reviews = db.relationship('Review', backref='manuscript', lazy=True)
    history = db.relationship('ManuscriptHistory',
                              backref='manuscript',
                              lazy=True,
                              order_by='ManuscriptHistory.created_at')


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    manuscript_id = db.Column(db.Integer, db.ForeignKey('manuscripts.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    text = db.Column(db.Text)
    score = db.Column(db.Integer)  # 1–5 или иной диапазон
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), nullable=False, default='pending')
    # pending, submitted, accepted, rejected

    # связь к пользователю-рецензенту (удобная ссылка)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])


class Publication(db.Model):
    __tablename__ = 'publications'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)  # journal, book, proceedings и т.п.
    title = db.Column(db.String(256), nullable=False)
    pub_date = db.Column(db.Date)
    description = db.Column(db.Text)

    manuscripts = db.relationship('Manuscript', backref='publication', lazy=True)


class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)

    # отправитель может быть как зарегистрированным пользователем,
    # так и анонимом (только email)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sender_email = db.Column(db.String(128), nullable=True)

    subject = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(16), default='new')  # new, done
    is_read = db.Column(db.Boolean, default=False)


class ManuscriptHistory(db.Model):
    """
    История изменений и комментариев по рукописям.
    Используется для хранения действий редактора/рецензента
    и отображения истории статусов автору.
    """
    __tablename__ = 'manuscript_history'

    id = db.Column(db.Integer, primary_key=True)

    manuscript_id = db.Column(db.Integer, db.ForeignKey('manuscripts.id'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # кто инициировал действие
    actor_role = db.Column(db.String(32), nullable=True)  # роль на момент действия (author/staff/reviewer/admin)

    action = db.Column(db.String(64), nullable=False)  # submitted/returned/accepted/rejected/comment и т.п.
    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
