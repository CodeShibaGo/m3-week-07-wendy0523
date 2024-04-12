from flask import render_template, flash, redirect, url_for,request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash,check_password_hash
from urllib.parse import urlsplit
from app import app,db
import sqlalchemy as sa
from datetime import datetime, timezone
from app.forms import EditProfileForm,EmptyForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm
from app.email import send_password_reset_email
from app.model import User,Post
import mysql.connector

# 連接 MySQL 資料庫
conn = mysql.connector.connect(
    host='localhost',  # 資料庫主機地址
    user='root',  # 資料庫使用者名稱
    password='112024112024',  # 資料庫密碼
    database='db_micrblog', # 資料庫名稱
    port=3306,
    auth_plugin='mysql_native_password'
)
cursor = conn.cursor()



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required

#避免用戶不小心多次提交表單的問題。
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('你的貼文現在已發布！')
        return redirect(url_for('index')) 
       
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

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
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)

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
    
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    
# @app.route('/explore')
# @login_required
# def explore():
#     page = request.args.get('page', 1, type=int)
#     per_page = app.config['POSTS_PER_PAGE']
    
#     # 計算 OFFSET 和 LIMIT
#     offset = (page - 1) * per_page
    
#     query = sa.text("""
#         SELECT * FROM post
#         ORDER BY timestamp DESC
#         LIMIT :limit OFFSET :offset
#     """)
    
#     posts = db.session.scalars(
#         query.bindparams(limit=per_page, offset=offset)
#     ).all()
    
#     # 獲取 post 總數
#     posts_count = db.session.scalar(sa.text("SELECT COUNT(*) FROM post"))
    
#     # 計算下一頁和上一頁的 URL
#     next_url = url_for('explore', page=page + 1) if (page * per_page) < posts_count else None
#     prev_url = url_for('explore', page=page - 1) if page > 1 else None
    
#     return render_template("index.html", title='Explore', posts=posts,
#                            next_url=next_url, prev_url=prev_url)
    
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('請檢查你的電子郵件以獲取重設密碼的指示')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='重設密碼', form=form)
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
