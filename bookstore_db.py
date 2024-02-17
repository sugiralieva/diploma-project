import sqlite3 as sq

class BookStoreDB:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    def create_table_books(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        description TEXT,
        price TEXT,
        category TEXT,
        image BLOB)''')
        self.db.commit()

    def create_table_users(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL)''')
        self.db.commit()

    def create_table_cart(self):
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            quantity INTEGER,
            user_id INTEGER NOT NULL)''')
            self.db.commit()
        except sq.Error as e:
            print('Ошибка создания таблицы cart' + str(e))

    def add_user(self, first_name, last_name, e_mail, password):
        # записываем данные о пользователе в таблицу users
        try:
            self.cursor.execute('INSERT INTO users(first_name, last_name, email, password) VALUES(?, ?, ?, ?)', (first_name, last_name, e_mail, password))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка подключения к БД' + str(e))


    def getUser(self, user_id):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT * FROM users WHERE id =? LIMIT 1', user_id)
            res = self.cursor.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except sq.Error as e:
            print('Ошибка получения данных из БД' + str(e))
        return False

    def get_user_email(self):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT email FROM users')
            res = self.cursor.fetchall()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка подключения к БД' + str(e))
        return False

    def get_user_by_email(self, e_mail):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute(f'''
        SELECT * FROM users WHERE email LIKE "{e_mail}" LIMIT 1''')
            res = self.cursor.fetchone()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка подключения к БД' + str(e))
        return False

    def change_password(self, new_password, e_mail):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute(f'UPDATE users SET password = ? WHERE email LIKE "{e_mail}"', (new_password,))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка подключения к ДБ' + str(e))

    def get_new_books(self):
        # получаем новые книги
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT id, title, price, image FROM books WHERE category="Романы" LIMIT 10')
            res = self.cursor.fetchall()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка получения категории из БД '+ str(e))
        return False

    def get_book_by_id(self, book_id):
        # получаем список книг для отображения в detail.html
        try:
            self.cursor.execute('SELECT title, price, description, image FROM books WHERE id=? LIMIT 1', (book_id,))
            res = self.cursor.fetchone()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка получения книги из БД '+ str(e))
        return False

    def get_books_by_category(self, cat, ):
        # получаем список книг для отображения в category.html
        try:

            self.cursor.execute('SELECT id, title, price, image FROM books WHERE category=?', (cat,))
            res = self.cursor.fetchall()
            return res
        except sq.Error as e:
            print('Ошибка получения книг по категории' + str(e))
        return False

    def add_book_to_cart(self, book_id, quantity, user_id):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('INSERT INTO cart(book_id, quantity, user_id) VALUES(?, ?, ?)', (book_id, quantity, user_id))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка записи данных в БД' + str(e))

    def get_book_ids_from_cart(self):
        ids = []
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT book_id FROM cart')
            res = self.cursor.fetchall()
            for r in res:
                ids.append(r[0])
            return ids
        except sq.Error as e:
            print('Ошибка получения book_id' + str(e))

    def update_quantity_of_books(self, book_id):
        try:
            self.cursor.execute('UPDATE cart SET quantity = quantity+1 WHERE book_id=?', (book_id,))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка обновления количества книг' + str(e))

    def get_all_books_in_cart(self, user_id):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute(f'''
SELECT image, title, quantity, price, quantity*price as total, book_id
FROM books 
JOIN cart 
ON books.id=cart.book_id
WHERE cart.user_id=?''', (user_id,))
            res = self.cursor.fetchall()
            return res
        except sq.Error as e:
            print('Ошибка подключения к БД' + str(e))
        return False


    def delete_book_from_cart(self, book_id, user_id):
        try:
            self.cursor.execute('DELETE FROM cart WHERE book_id=? AND user_id=?', (book_id, user_id))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка удаления книги из корзины' + str(e))

    def clear_cart(self):
        try:
            self.cursor.execute('DELETE FROM cart')
            self.db.commit()
        except sq.Error as e:
            print('Ошибка подключения к БД' + str(e))

    def create_table_orders(self):
        try:
            self.cursor.execute('''
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
zip TEXT NOT NULL,
street TEXT NOT NULL,
city TEXT NOT NULL,
country TEXT NOT NULL,
phone TEXT NOT NULL,
e_mail TEXT NOT NULL,
customer_order TEXT NOT NULL)''')
            self.db.commit()
        except sq.Error as e:
            print('Ошибка создания таблицы orders' + str(e))

    def add_order(self, user_id, zip_address, street, city, country, phone, e_mail, order):
        try:
            self.cursor.execute('INSERT INTO orders(user_id, zip, street, city, country, phone, e_mail, customer_order) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (user_id, zip_address, street, city, country, phone, e_mail, order))
            self.db.commit()
        except sq.Error as e:
            print('Ошибка записи данных в БД' + str(e))

    def get_two_posts(self):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT id, title, author, short_post FROM blog LIMIT 2')
            res = self.cursor.fetchall()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка получения данных из blog' + str(e))
        return False

    def get_all_posts(self):
        # with sq.connect(self.db) as con:
        #     self.cursor = con.cursor()
        try:
            self.cursor.execute('SELECT id, title, author, image, short_post, publication_date FROM blog')
            res = self.cursor.fetchall()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка получения данных из blog' + str(e))
        return False

    def get_post_by_id(self, post_id):
        try:
            self.cursor.execute('SELECT title, author, post, image, publication_date FROM blog WHERE id=? LIMIT 1', (post_id,))
            res = self.cursor.fetchone()
            if res:
                return res
        except sq.Error as e:
            print('Ошибка получения поста из БД '+ str(e))
        return False



# db = BookStoreDB('bookstore.db')
# user = db.get_all_books_in_cart(1)
# print(user)
