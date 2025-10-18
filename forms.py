from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

# --- Форма входа ---
class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=128)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# --- Форма регистрации ---
class RegistrationForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(max=128)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=128)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Повторите пароль', validators=[
        DataRequired(), EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')

# --- Форма подачи рукописи ---
class ManuscriptForm(FlaskForm):
    title = StringField('Название рукописи', validators=[DataRequired(), Length(max=256)])
    description = TextAreaField('Описание (аннотация)', validators=[Length(max=2000)])
    file = FileField('Файл рукописи', validators=[DataRequired()])
    submit = SubmitField('Отправить')

# --- Форма рецензии ---
class ReviewForm(FlaskForm):
    text = TextAreaField('Текст рецензии', validators=[DataRequired(), Length(max=4000)])
    score = IntegerField('Оценка (1-5)', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# --- Форма обратной связи/контакта ---
class ContactForm(FlaskForm):
    subject = StringField('Тема обращения', validators=[DataRequired(), Length(max=256)])
    body = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Отправить')

# --- Форма новостей (для админки/редактора) ---
class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=256)])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
