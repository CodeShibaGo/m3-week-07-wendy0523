from flask import render_template
from flask_mail import Message
from app import mail, app
from threading import Thread

#非同步發送電子郵件的函數，不影響主應用性能跟時間
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# 郵件寄送函數  (郵件的主題,發件人郵件地址,收件人郵件地址列表，內容，html內容)
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] 重設您的密碼',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.html',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))