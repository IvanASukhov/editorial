from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_from_directory, abort, current_app
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from models import db, User, Manuscript, Review, Publication, News, Message

routes = Blueprint('routes', __name__)

# --- Вспомогательные функции ---

def current_user():
    uid = session.get('user_id')
    if uid:
        return User.query.get(uid)
    return None

def login_required(role=None):
    def wrapper(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Для доступа требуется вход.", "warning")
                return redirect(url_for('routes.login'))
            if role and user.role != role:
                flash("Недостаточно прав.", "danger")
                return redirect(url_for('routes.index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# --- Главная страница, новости, публикации (публичная часть) ---

@routes.route('/')
def index():
    news = News.query.order_by(News.published_at.desc()).all()
    publications = Publication.query.order_by(Publication.pub_date.desc()).all()
    return render_template('index.html', news=news, publications=publications, user=current_user())

@routes.route('/news')
def news():
    all_news = News.query.order_by(News.published_at.desc()).all()
    return render_template('news/news.html', news=all_news, user=current_user())

@routes.route('/news/<int:news_id>')
def news_detail(news_id):
    item = News.query.get_or_404(news_id)
    return render_template('news/news_detail.html', item=item, user=current_user())

@routes.route('/publications')
def publications():
    pubs = Publication.query.order_by(Publication.pub_date.desc()).all()
    return render_template('publications/publication_list.html', publications=pubs, user=current_user())

@routes.route('/publications/<int:pub_id>')
def publication_detail(pub_id):
    pub = Publication.query.get_or_404(pub_id)
    manuscripts = Manuscript.query.filter_by(publication_id=pub.id, status="published").all()
    return render_template('publications/publication_detail.html', publication=pub, manuscripts=manuscripts, user=current_user())

# --- Аутентификация ---

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Вы успешно вошли.', 'success')
            return redirect(url_for('routes.profile'))
        flash('Неверные email или пароль.', 'danger')
    return render_template('auth/login.html')

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Выход выполнен.', 'info')
    return redirect(url_for('routes.index'))

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'author'
        if User.query.filter_by(email=email).first():
            flash('Такой email уже зарегистрирован.', 'danger')
            return redirect(url_for('routes.register'))
        from werkzeug.security import generate_password_hash
        user = User(full_name=full_name, email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна. Войдите.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('auth/register.html')

# --- Личный кабинет пользователя ---

@routes.route('/profile')
@login_required()
def profile():
    user = current_user()
    my_manuscripts = Manuscript.query.filter_by(author_id=user.id).order_by(Manuscript.created_at.desc()).all() if user.role == 'author' else []
    my_reviews = Review.query.filter_by(reviewer_id=user.id).order_by(Review.created_at.desc()).all() if user.role == 'reviewer' else []
    return render_template('auth/profile.html', user=user, manuscripts=my_manuscripts, reviews=my_reviews)

# --- Подача рукописи автором ---

@routes.route('/manuscripts/submit', methods=['GET', 'POST'])
@login_required('author')
def submit_manuscript():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files['file']
        if not title or not file:
            flash('Укажите название и приложите файл.', 'danger')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        save_path = os.path.join('media', 'manuscripts', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
        manuscript = Manuscript(
            title=title,
            description=description,
            file_path=save_path,
            status='submitted',
            author_id=current_user().id
        )
        db.session.add(manuscript)
        db.session.commit()
        flash('Рукопись отправлена на рассмотрение!', 'success')
        return redirect(url_for('routes.manuscript_status'))
    return render_template('manuscripts/submit_manuscript.html', user=current_user())

@routes.route('/manuscripts/status')
@login_required('author')
def manuscript_status():
    user = current_user()
    manuscripts = Manuscript.query.filter_by(author_id=user.id).order_by(Manuscript.created_at.desc()).all()
    return render_template('manuscripts/manuscript_status.html', manuscripts=manuscripts, user=user)

# --- Просмотр всех рукописей (редактор, рецензент) ---

@routes.route('/manuscripts')
@login_required()
def manuscript_list():
    user = current_user()
    if user.role == 'staff':
        manuscripts = Manuscript.query.order_by(Manuscript.created_at.desc()).all()
    elif user.role == 'reviewer':
        manuscripts = [r.manuscript for r in Review.query.filter_by(reviewer_id=user.id).all()]
    else:
        abort(403)
    return render_template('manuscripts/manuscript_list.html', manuscripts=manuscripts, user=user)

# --- Добавление/просмотр рецензии (рецензент) ---

@routes.route('/reviews/<int:manuscript_id>', methods=['GET', 'POST'])
@login_required('reviewer')
def review_form(manuscript_id):
    manuscript = Manuscript.query.get_or_404(manuscript_id)
    user = current_user()
    review = Review.query.filter_by(manuscript_id=manuscript.id, reviewer_id=user.id).first()
    if request.method == 'POST':
        text = request.form.get('text')
        score = request.form.get('score')
        if not review:
            review = Review(
                manuscript_id=manuscript.id,
                reviewer_id=user.id,
                text=text,
                score=int(score),
                status='submitted'
            )
            db.session.add(review)
        else:
            review.text = text
            review.score = int(score)
            review.status = 'submitted'
        db.session.commit()
        flash('Рецензия сохранена.', 'success')
        return redirect(url_for('routes.manuscript_list'))
    return render_template('reviews/review_form.html', manuscript=manuscript, review=review, user=user)

@routes.route('/reviews/list/<int:manuscript_id>')
@login_required('staff')
def review_list(manuscript_id):
    manuscript = Manuscript.query.get_or_404(manuscript_id)
    reviews = Review.query.filter_by(manuscript_id=manuscript.id).all()
    return render_template('reviews/review_list.html', manuscript=manuscript, reviews=reviews, user=current_user())

# ===========================
# ====== НОВАЯ АДМИНКА ======
# ===========================

from sqlalchemy import func

# --- Админ-панель (dashboard) ---
@routes.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    # Краткая статистика
    stats = {
        'news_total': News.query.count(),
        'publications_total': Publication.query.count(),
        'users_total': User.query.count(),
        'contacts_new': Message.query.filter_by(status='new').count() if hasattr(Message, 'status') else 0,
    }
    # последние 5
    contacts = Message.query.order_by(Message.sent_at.desc()).limit(5).all()
    news = News.query.order_by(News.published_at.desc()).limit(5).all()
    publications = Publication.query.order_by(Publication.pub_date.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, contacts=contacts, news=news, publications=publications, user=current_user())

# --- Новости (список, добавление, редактирование, удаление) ---
@routes.route('/admin/news', methods=['GET', 'POST'])
@login_required('admin')
def admin_news():
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            news_id = request.form.get('news_id')
            news = News.query.get(news_id)
            if news:
                db.session.delete(news)
                db.session.commit()
                flash('Новость удалена.', 'info')
            return redirect(url_for('routes.admin_news'))
    news_list = News.query.order_by(News.published_at.desc()).all()
    return render_template('admin/news_list.html', news_list=news_list, user=current_user())

@routes.route('/admin/news/edit', defaults={'news_id': None}, methods=['GET', 'POST'])
@routes.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_news_edit(news_id):
    news = News.query.get(news_id) if news_id else None
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if not title or not content:
            flash('Заполните все поля.', 'danger')
            return redirect(request.url)
        if news:
            news.title = title
            news.content = content
            if not news.published_at:
                news.published_at = datetime.now()
        else:
            news = News(title=title, content=content, published_at=datetime.now())
            db.session.add(news)
        db.session.commit()
        flash('Новость сохранена.', 'success')
        return redirect(url_for('routes.admin_news'))
    return render_template('admin/news_edit.html', news=news, user=current_user())

# --- Публикации (список, добавление, редактирование, удаление) ---
@routes.route('/admin/publications', methods=['GET', 'POST'])
@login_required('admin')
def admin_publications():
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            pub_id = request.form.get('pub_id')
            pub = Publication.query.get(pub_id)
            if pub:
                db.session.delete(pub)
                db.session.commit()
                flash('Публикация удалена.', 'info')
            return redirect(url_for('routes.admin_publications'))
    publications = Publication.query.order_by(Publication.pub_date.desc()).all()
    return render_template('admin/publications_list.html', publications=publications, user=current_user())

@routes.route('/admin/publications/edit', defaults={'pub_id': None}, methods=['GET', 'POST'])
@routes.route('/admin/publications/edit/<int:pub_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_publications_edit(pub_id):
    publication = Publication.query.get(pub_id) if pub_id else None
    if request.method == 'POST':
        title = request.form.get('title')
        pub_type = request.form.get('type')
        pub_date = request.form.get('pub_date') or None
        description = request.form.get('description')
        if not title or not pub_type:
            flash('Заполните все обязательные поля.', 'danger')
            return redirect(request.url)
        if pub_date:
            try:
                pub_date = datetime.strptime(pub_date, '%Y-%m-%d').date()
            except ValueError:
                pub_date = None
        if publication:
            publication.title = title
            publication.type = pub_type
            publication.pub_date = pub_date
            publication.description = description
        else:
            publication = Publication(
                title=title,
                type=pub_type,
                pub_date=pub_date,
                description=description
            )
            db.session.add(publication)
        db.session.commit()
        flash('Публикация сохранена.', 'success')
        return redirect(url_for('routes.admin_publications'))
    return render_template('admin/publications_edit.html', publication=publication, user=current_user())

# --- Пользователи (список, просмотр, смена роли, блокировка/разблокировка) ---
@routes.route('/admin/users')
@login_required('admin')
def admin_users():
    q = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()
    users_query = User.query
    if q:
        users_query = users_query.filter((User.full_name.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%')))
    if role:
        users_query = users_query.filter_by(role=role)
    users = users_query.order_by(User.registered_at.desc()).all()
    return render_template('admin/users_list.html', users=users, user=current_user())

@routes.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_user_edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_role':
            new_role = request.form.get('role')
            if new_role and new_role != user.role:
                user.role = new_role
                db.session.commit()
                flash('Роль пользователя обновлена.', 'success')
        elif action == 'block':
            user.is_blocked = True
            db.session.commit()
            flash('Пользователь заблокирован.', 'info')
        elif action == 'unblock':
            user.is_blocked = False
            db.session.commit()
            flash('Пользователь разблокирован.', 'success')
        return redirect(url_for('routes.admin_user_edit', user_id=user.id))
    return render_template('admin/user_edit.html', user=user, user_viewer=current_user())

# --- Обращения (контакты/обратная связь) ---
@routes.route('/admin/contacts', methods=['GET', 'POST'])
@login_required('admin')
def admin_contacts():
    if request.method == 'POST':
        contact_id = request.form.get('contact_id')
        action = request.form.get('action')
        msg = Message.query.get(contact_id)
        if msg and action == 'mark_done':
            msg.status = 'done'
            db.session.commit()
            flash('Обращение отмечено как обработанное.', 'success')
        return redirect(url_for('routes.admin_contacts'))
    contacts = Message.query.order_by(Message.sent_at.desc()).all()
    return render_template('admin/contacts_list.html', contacts=contacts, user=current_user())

# --- Отчёты и аналитика ---
@routes.route('/admin/reports')
@login_required('admin')
def admin_reports():
    stats = {
        'users_total': User.query.count(),
        'users_authors': User.query.filter_by(role='author').count(),
        'users_staff': User.query.filter_by(role='staff').count(),
        'users_reviewers': User.query.filter_by(role='reviewer').count(),
        'users_admins': User.query.filter_by(role='admin').count(),
        'publications_total': Publication.query.count(),
        'manuscripts_total': Manuscript.query.count(),
        'published_manuscripts': Manuscript.query.filter_by(status='published').count(),
        'in_review': Manuscript.query.filter_by(status='under_review').count(),
        'contacts_total': Message.query.count(),
        'contacts_new': Message.query.filter_by(status='new').count() if hasattr(Message, 'status') else 0,
        'contacts_done': Message.query.filter_by(status='done').count() if hasattr(Message, 'status') else 0,
    }
    return render_template('admin/reports.html', stats=stats, user=current_user())

# --- Загрузка файлов (рукописи, рецензии) ---

@routes.route('/media/<path:filename>')
@login_required()
def media(filename):
    dirpath = os.path.join(current_app.root_path, 'media')
    return send_from_directory(directory=dirpath, filename=filename, as_attachment=True)

# --- Контакты, обратная связь (для пользователей) ---

@routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sender = current_user()
        # поддержка анонимных обращений
        sender_email = request.form.get('email') if not sender else None
        subject = request.form.get('subject')
        body = request.form.get('body')
        if (sender or sender_email) and subject and body:
            msg = Message(
                sender_id=sender.id if sender else None,
                sender_email=sender_email,
                subject=subject,
                body=body,
                sent_at=datetime.now(),
                status='new'
            )
            db.session.add(msg)
            db.session.commit()
            flash('Сообщение отправлено.', 'success')
        else:
            flash('Заполните все поля.', 'danger')
    return render_template('contact.html', user=current_user())

# --- Обработка 404 ---

@routes.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', user=current_user()), 404

