from flask import Flask, render_template, request, session, url_for, redirect, flash
from database.database import init_db
from database.manager import UserManager, BookManager, OrderManager, PostManager
from database.database import db_session
from database.models import User, Book, Order, Post
from werkzeug import secure_filename
import datetime
import os

app = Flask(__name__)
app.secret_key = "bookstore secret_key"

UPLOAD_FOLDER = '/static/image/Book'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create table if not exists
init_db()


@app.route('/')
def root():
    return render_template('Login/registration.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    id = str(request.form['memberId'])
    password = str(request.form['memberPass'])
    name = str(request.form['memberName'])
    phone_number = str(request.form['memberNumber'])
    address = str(request.form['memberAddress'])

    user = User(id, password, name, phone_number, address)
    if not UserManager.sign_in(user):
        sign_in_result = '해당 ID가 이미 존재합니다.'
    else:
        session['user_id'] = id
        sign_in_result = '회원가입에 성공하였습니다. 로그인해 주세요 :)'
    return render_template('Login/registration.html', sign_in_result=sign_in_result)


@app.route('/login', methods=['GET', 'POST'])
def login():
    id = str(request.form['memberId'])
    password = str(request.form['memberPass'])
    is_admin = db_session.query(User.admin).filter_by(id=id).one()[0]

    if not UserManager.log_in(id, password):
        login_error = '아이디 혹은 비밀번호가 일치하지 않습니다.'
    else:
        session['user_id'] = id
        session['user_name'] = UserManager.get_name(id)
        if is_admin == '1':
            return redirect(url_for('admin_main'))
        else:
            return redirect(url_for('main'))
    return render_template('Login/registration.html', login_error=login_error)


@app.route('/main')
def main():
    book_list = Book.query.order_by(Book.date).all()
    count = len(book_list)
    return render_template('Main/main.html', book_list=book_list, count=count, sort_type='Date')


@app.route('/main_sort', methods=['GET', 'POST'])
def main_sort():
    sort_type = str(request.form['sort'])
    book_list = BookManager.get_book_list(sort_type)
    count = BookManager.get_book_all_counts()

    return render_template('Main/main.html', book_list=book_list, count=count, sort_type=sort_type)


@app.route('/my_room')
def my_room():
    user_id = session['user_id']
    order_list = Order.query.filter_by(user_id=user_id).order_by(Order.date).all()
    owned_point = int(db_session.query(User.point).filter_by(id=session['user_id']).one()[0])

    my_room_list = list()
    for order in order_list:
        temp_list = list()
        temp_list.append(db_session.query(Book.name).filter_by(id=order.book_id).one()[0])
        temp_list.append(order.date)
        temp_list.append(db_session.query(Book.price).filter_by(id=order.book_id).one()[0])
        my_room_list.append(temp_list)
    return render_template('Main/my_room.html', my_room_list=my_room_list, owned_point=owned_point)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    check_list = request.form.getlist('checkbox')
    payment_list = list()
    total_price = 0
    total_point = 0
    owned_point = int(db_session.query(User.point).filter_by(id=session['user_id']).one()[0])

    for element in check_list:
        temp_list = list()
        temp_list.append(db_session.query(Book.image).filter_by(id=str(element)).one()[0])
        temp_list.append(db_session.query(Book.name).filter_by(id=str(element)).one()[0])

        price = db_session.query(Book.price).filter_by(id=str(element)).one()[0]
        point = int(price * 0.1)

        total_price += price
        total_point += point

        temp_list.append('{:0,.0f}'.format(price))
        temp_list.append('{:0,.0f}'.format(point))
        temp_list.append(db_session.query(Book.id).filter_by(id=str(element)).one()[0])

        payment_list.append(temp_list)

    return render_template('Main/payment.html',payment_list=payment_list, total_price=total_price, total_point=total_point, owned_point=owned_point)


@app.route('/payment_approve', methods=['GET', 'POST'])
def payment_approve():
    payment_list = request.form.getlist('payment_list')
    total_point = request.form['total_point']
    total_price = request.form['total_price']
    is_check_using_point = str(request.form.getlist('check_box'))
    flag = ''

    if is_check_using_point[0] is not None:
        for element in is_check_using_point:
            flag += element

    if flag == "['True']":
        if not UserManager.use_point(total_price, session['user_id']):
            return render_template('Main/payment.html', messege='포인트가 부족하여 구매를 할수 없습니다 :[')
    else:
        UserManager.update_point(total_point, session['user_id'])

    for element in payment_list:
        order = Order(session['user_id'], element, datetime.datetime.now())
        OrderManager.insert_order(order)

    return redirect(url_for('my_room'))


@app.route('/admin_main')
def admin_main():
    return render_template('Admin/admin_main.html')


@app.route('/admin_date')
def admin_date():
    book_list = OrderManager.get_admin_date()
    return render_template('Admin/Sales/date.html', book_list=book_list)


@app.route('/admin_user')
def admin_user():
    book_list = OrderManager.get_admin_user()
    return render_template('Admin/Sales/user.html', book_list=book_list)


@app.route('/admin_book')
def admin_book():
    book_list = OrderManager.get_admin_book()
    return render_template('Admin/Sales/book.html', book_list=book_list)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/admin_book_manage')
def admin_manage():
    book_list = Book.query.order_by(Book.id).all()
    return render_template('Admin/BookManage/manage.html', book_list=book_list)


@app.route('/uploaded_file', methods=['GET', 'POST'])
def uploaded_file():
    book_title = str(request.form['book_title'])
    book_price = str(request.form['book_price'])
    book_publisher = str(request.form['book_publisher'])

    book = Book(book_title, book_price, book_publisher, 'test.png')
    BookManager.insert_book(book)
    return redirect(url_for('admin_manage'))


@app.route('/delete_book', methods=['GET', 'POST'])
def delete_book():
    book_id_list = str(request.form.getlist('book_id'))

    book_id_list = book_id_list.replace('[', '')
    book_id_list = book_id_list.replace(']', '')
    book_id_list = book_id_list.replace('\'', '')
    book_id_list = book_id_list.split(',')

    for book_id in book_id_list:
        BookManager.delete_book(book_id)

    return redirect(url_for('admin_manage'))


@app.route('/post_view')
def post_view():
    post_list = Post.query.order_by(Post.date).all()
    return render_template('Main/post_view.html', post_list=post_list)


@app.route('/post_write')
def post_write():
    return render_template('Main/post_write.html')


@app.route('/approval_write', methods=['GET', 'POST'])
def approval_write():
    contents = str(request.form['contents'])
    post = Post(session['user_id'], contents)
    PostManager.insert_post(post)
    return redirect(url_for('post_view'))

if __name__ == '__main__':
    app.run(debug=True)
    app.run()
