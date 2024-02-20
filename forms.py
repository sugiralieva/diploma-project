from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class Register(FlaskForm):
    first_name = StringField('Имя: ', validators=[DataRequired(),
                                            Length(min=2, max=20, message='Имя должно состоять от 2 до 20 символов')])
    last_name = StringField('Фамилия: ', validators=[DataRequired(),
                                            Length(min=2, max=20, message='Фамилия должна состоять от 2 до 20 символов')])
    e_mail = StringField('Email: ', validators=[Email(message='Некорректный email')])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=5, max=20)])
    password2 = PasswordField('Повторите пароль: ', validators=[EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField('Зарегистрироваться')


class LogIn(FlaskForm):
    e_mail = StringField('Email: ', validators=[Email(message='Некорректный email')])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=5, max=20)])
    remember = BooleanField(label='запомнить меня', default=False)
    submit = SubmitField('Войти')


class ChangePassword(FlaskForm):
    old_password = PasswordField('Старый пароль: ', validators=[DataRequired(), Length(min=5, max=20)])
    new_password = PasswordField('Новый пароль: ', validators=[DataRequired(), Length(min=5, max=20)])
    repeat_new_password = PasswordField('Повторите пароль: ', validators=[EqualTo('new_password', message='Пароли не совпадают')])
    submit = SubmitField('Сменить пароль')

class Order(FlaskForm):
    zip_address = StringField('Индекс: ', validators=[DataRequired(), Length(min=4, max=10)])
    street = StringField('Улица, дом: ', validators=[DataRequired(), Length(min=4, max=50)])
    city = StringField('Город: ', validators=[DataRequired(), Length(min=2, max=20)])
    country = StringField('Страна: ', validators=[DataRequired(), Length(min=4, max=20)])
    phone = StringField('Телефон: ', validators=[DataRequired(), Length(min=6, max=20)])
    e_mail = StringField('Email: ', validators=[Email(message='Некорректный email')])
    submit = SubmitField('Заказать')

class Search(FlaskForm):
    text = StringField('Поиск: ', validators=[DataRequired()])
    search = SubmitField('Поиск')

class Subscribe(FlaskForm):
    e_mail = StringField('Email: ', validators=[Email(message='Некорректный email')])
    subscribe = SubmitField('Подписаться!')
