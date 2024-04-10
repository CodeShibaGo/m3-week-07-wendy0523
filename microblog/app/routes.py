from flask import render_template, flash, redirect, url_for,request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlsplit
from app import app,db
import sqlalchemy as sa
from datetime import datetime, timezone
from app.forms import EditProfileForm
from app.model import User
import mysql.connector

# 連接 MySQL 資料庫
conn = mysql.connector.connect(
    host='localhost',  # 資料庫主機地址
    user='root',  # 資料庫使用者名稱
    password='112024112024',  # 資料庫密碼
    database='db_micrblog', # 資料庫名稱
    port=3306
)
cursor = conn.cursor()



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required

def index():
    user = {'username': 'Wendy'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Portland 的天氣真好！'
        },
        {
            'author': {'username': 'Susan'},
            'body': '復仇者聯盟電影真的很酷！'
        },
        {
            'author': {'username': 'John'},
            'body': '沙丘2很好看！'
        }

    ]
    return render_template('index.html', title='首頁',posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    username_error = None
    password_error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('rememberMe')

        username_error = None if username else "此欄位不得為空"
        password_error = None if password else "此欄位不得為空"

        user = db.session.query(User).filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('無效的使用者名稱或密碼')
        else:
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)

    return render_template('login.html', title='登入', username_error=username_error, password_error=password_error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method =='POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            password_error = "密碼不符" 
            return render_template('register.html', title='Register', password_error=password_error)
        hashed_password = generate_password_hash(password)
        
        sql = "INSERT INTO user (username, email, password_hash) VALUES (%s, %s, %s)"
        val = (username, email, hashed_password)
        cursor.execute(sql, val)
        # 提交事務
        conn.commit()
        flash('註冊成功')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': '測試貼文 #1'},
        {'author': user, 'body': '測試貼文 #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)