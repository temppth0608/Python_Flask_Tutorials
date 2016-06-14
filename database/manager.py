from sqlalchemy import func

from database.models import User, Book, Order, Post
from database.database import init_db
from database.database import db_session

init_db()


class UserManager:

    @staticmethod
    def sign_in(user):
        db_session.remove()
        if User.query.get(user.id) is None:
            db_session.add(user)
            db_session.commit()
            print(db_session)
            return True
        else:
            return False

    @staticmethod
    def log_in(user_id, user_password):
        db_session.remove()
        result = User.query.get(user_id)

        if result is None:
            return False
        else:
            if db_session.query(User.password).filter_by(id=user_id).one()[0] == user_password:
                return True
            else:
                return False

    @staticmethod
    def update_point(point, user_id):
        user = User.query.filter_by(id=user_id).first()
        user.point += int(point)
        db_session.commit()

    @staticmethod
    def use_point(price, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user.point < int(price):
            return False
        else:
            user.point -= int(price)
            db_session.commit()
            return True

    @staticmethod
    def get_name(user_id):
        return db_session.query(User.name).filter_by(id=user_id).one()[0]


class BookManager:

    @staticmethod
    def get_book_all_counts():
        return len(Book.query.all())

    @staticmethod
    def get_book_list(sort_type):
        if sort_type == 'Date':
            book_list = Book.query.order_by(Book.date).all()
        elif sort_type == 'Publisher':
            book_list = Book.query.order_by(Book.publisher).all()
        elif sort_type == 'Price':
            book_list = Book.query.order_by(Book.price).all()
        else:
            book_list = Book.query.order_by(Book.name).all()
        return book_list

    @staticmethod
    def insert_book(book):
        db_session.add(book)
        db_session.commit()

    @staticmethod
    def delete_book(book_id):
        db_session.query(Book).filter_by(id=book_id).delete()
        db_session.commit()


class OrderManager:

    @staticmethod
    def insert_order(order):
        db_session.add(order)
        db_session.commit()

    @staticmethod
    def get_admin_date():
        book_list = db_session.\
            query(Order.date, Book.name, func.count(Order.date))\
            .join(Book)\
            .group_by(func.DATE(Order.date)).distinct()\
            .order_by(Order.date)\
            .all()

        return book_list

    @staticmethod
    def get_admin_user():
        book_list = db_session.\
            query(Order.user_id, func.count(Order.user_id))\
            .group_by(Order.user_id).all()

        return book_list

    @staticmethod
    def get_admin_book():
        book_list = db_session.\
            query(Order.book_id,Book.name, func.count(Order.book_id))\
            .join(Book)\
            .group_by(Order.book_id).all()

        return book_list


class PostManager:

    @staticmethod
    def insert_post(post):
        db_session.add(post)
        db_session.commit()