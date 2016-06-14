from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from database.database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(String(20), primary_key=True)
    password = Column(String(20), nullable=False)
    name = Column(String(20), nullable=False)
    phoneNumber = Column(String(40), nullable=True)
    address = Column(String(300), nullable=True)
    point = Column(Integer, nullable=True)
    admin = Column(String(1), nullable=False)

    def __init__(self, user_id, password, name, phone_number, address, point):
        self.id = user_id
        self.password = password
        self.name = name
        self.phoneNumber = phone_number
        self.address = address
        self.point = point
        self.admin = '0'

    def __repr__(self):
        return '<User %r, %r>' % (self.id, self.name)


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)
    publisher = Column(String(200), nullable=False)
    image = Column(String(300), nullable=False)
    date = Column(String(20), nullable=False, default=func.now())

    def __init__(self, name, price, publisher, image):
        self.name = name
        self.price = price
        self.publisher = publisher
        self.image = image

    def __repr__(self):
        return '<Book %r, %r>' % (self.id, self.publisher)


class Order(Base):
    __tablename__ = 'order'
    order_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String(20), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'),nullable=False)
    date = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, user_id, book_id, date):
        self.user_id = user_id
        self.book_id = book_id
        self.date = date

    def __repr__(self):
        return '<Order %r, %r>' % (self.order_id, self.book_id)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String(20), primary_key=True)
    contents = Column(String(1000), nullable=True)
    date = Column(String(20), nullable=False, default=func.now())

    def __init__(self, user_id, contents):
        self.user_id = user_id
        self.contents = contents

    def __repr__(self):
        return '<Post %r %r>' % (self.id, self.contents)