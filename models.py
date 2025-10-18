from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Ассоциация ролей: Автор, Сотрудник, Рецензент, Администратор
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # author, staff, reviewer, admin
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    manuscripts = db.relationship('Manuscript', backref='author', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

class Manuscript(db.Model):
    __tablename__ = 'manuscripts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(32), nullable=False, default='submitted')  # submitted, under_review, accepted, rejected, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'), nullable=True)
    reviews = db.relationship('Review', backref='manuscript', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    manuscript_id = db.Column(db.Integer, db.ForeignKey('manuscripts.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text)
    score = db.Column(db.Integer)  # 1-5 или иной диапазон
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), nullable=False, default='pending')  # pending, submitted, accepted, rejected

    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

class Publication(db.Model):
    __tablename__ = 'publications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)  # journal, book, proceedings
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
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(256))
    body = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
