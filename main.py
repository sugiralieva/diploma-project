from base64 import b64encode
import datetime
from functools import reduce
from flask import Flask
from flask import render_template, url_for, request, flash, session, redirect, abort, g, sessions
from flask_paginate import Pagination, get_page_parameter
import sqlite3 as sq
import os
from bookstore_db import BookStoreDB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import Register, LogIn, ChangePassword, Order
from User_login import UserLogin

DATABASE = 'bookstore.db'
DEBUG = True
SECRET_KEY = 'fdgdfgdfggf786hfg6hfg6h7f'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'bookstore.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'


nav_bar = [{'main': 'Художественная литература', 'sub': ['Фантастика', 'Детективы', 'Романы', 'Ужасы', 'Манга, комиксы']},
           {'main': 'Научно-популярная литература', 'sub': ['Деловая литература', 'Медицина и здоровье', 'Спорт и туризм', 'Компьютеры и Интернет', 'Юридическая литература']},
           {'main': 'Детская литература', 'sub': ['Сказки', 'Приключения', 'Познавательная литература']}]


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sq.connect(app.config['DATABASE'])
    conn.row_factory = sq.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = BookStoreDB(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    new_books = dbase.get_new_books()
    new_books = list(map(lambda i: list(i), new_books))
    for image in new_books:
        image[3] = b64encode(image[3]).decode("utf-8")
    return render_template('index.html', nav_bar=nav_bar, new_books=new_books)


@app.route('/detail/<int:book_id>', methods=['GET', 'POST'])
@login_required
def detail(book_id):
    dbase.create_table_cart()
    title, price, description, image = dbase.get_book_by_id(book_id)
    image = b64encode(image).decode("utf-8")

    if request.method == 'POST':
        book_ids_from_cart = dbase.get_book_ids_from_cart()
        if book_id in book_ids_from_cart:
            dbase.update_quantity_of_books(book_id)
        else:
            dbase.add_book_to_cart(book_id, 1, current_user.get_id())
        flash('Добавлено в корзину!')

    new_books = dbase.get_new_books()
    new_books = list(map(lambda i: list(i), new_books))
    for img in new_books:
        img[3] = b64encode(img[3]).decode("utf-8")
    return render_template('detail.html', nav_bar=nav_bar, book_id=book_id, title=title, price=price, description=description, image=image, new_books=new_books)


@app.route('/category/<string:cat>')
def category(cat):
    books_in_category = dbase.get_books_by_category(cat)
    books_in_category = list(map(lambda i: list(i), books_in_category))
    for image in books_in_category:
        image[3] = b64encode(image[3]).decode("utf-8")
    return render_template('category.html', nav_bar=nav_bar, books_in_category=books_in_category)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    books_in_cart = dbase.get_all_books_in_cart(current_user.get_id())
    books_in_cart = list(map(lambda i: list(i), books_in_cart))

    for image in books_in_cart:
        image[0] = b64encode(image[0]).decode("utf-8")
    prices = [int(price[4]) for price in books_in_cart]
    total = reduce(lambda x, y: x+y, prices, 0)
    if request.method == 'POST':
        dbase.delete_book_from_cart(request.form.get('delete'), current_user.get_id())
        return redirect(url_for('cart'))
    print(request.form.get('delete'))
    return render_template('cart.html', nav_bar=nav_bar, books_in_cart=books_in_cart, total=total)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    books_in_cart = dbase.get_all_books_in_cart(current_user.get_id())
    prices = [int(price[4]) for price in books_in_cart]
    total = reduce(lambda x, y: x + y, prices, 0)
    form = Order()
    return render_template('checkout.html', nav_bar=nav_bar, total=total, form=form)


@app.route('/customer-order', methods=['GET', 'POST'])
def customer_order():
    return render_template('customer-order.html', nav_bar=nav_bar)


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    return render_template('blog.html', nav_bar=nav_bar)


@app.route('/post', methods=['GET', 'POST'])
def post():
    return render_template('post.html', nav_bar=nav_bar)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        dbase.create_table_users()
        emails = dbase.get_user_email()
        if emails:
            emails = [i for i in emails[0]]
            if form.e_mail.data in emails:
                flash('Этот email уже зарегистрирован, используйте другой email для регистрации', category='error')
            else:
                dbase.add_user(form.first_name.data, form.last_name.data, form.e_mail.data, password_hash)
                flash('Вы успешно зарегистрированы!', category='success')
        else:
            dbase.add_user(form.first_name.data, form.last_name.data, form.e_mail.data, password_hash)
            flash('Вы успешно зарегистрированы!', category='success')
    return render_template('register.html', nav_bar=nav_bar, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogIn()
    if current_user.is_authenticated:
        return redirect(url_for('customer_account'))

    if form.validate_on_submit():
        user = dbase.get_user_by_email(form.e_mail.data)
        if user and check_password_hash(user['password'], form.password.data):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('customer_account'))
        flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html', nav_bar=nav_bar, form=form)

@app.route('/customer-account', methods=['GET', 'POST'])
@login_required
def customer_account():
    form = ChangePassword()

    if form.validate_on_submit():
        user = dbase.get_user_by_email(current_user.getEmail())
        if user and check_password_hash(user['password'], form.old_password.data):
            new_password_hash = generate_password_hash(form.new_password.data)
            dbase.change_password(new_password_hash, current_user.getEmail())
            flash('Пароль был изменен!', category='success')
        else:
            flash('Пароли не совпадают!', category='error')

    return render_template('customer-account.html', nav_bar=nav_bar, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    return render_template('faq.html', nav_bar=nav_bar)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', nav_bar=nav_bar)


@app.route('/404', methods=['GET', 'POST'])
def error():
    return render_template('404.html', nav_bar=nav_bar)


if __name__ == '__main__':
    app.run(debug=True)