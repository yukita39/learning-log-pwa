# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from db import Session, User

class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名', 
                         validators=[DataRequired(message='ユーザー名を入力してください'), 
                                   Length(min=3, max=20, message='3文字以上20文字以下で入力してください')])
    email = StringField('メールアドレス', 
                       validators=[DataRequired(message='メールアドレスを入力してください'), 
                                 Email(message='有効なメールアドレスを入力してください')])
    password = PasswordField('パスワード', 
                           validators=[DataRequired(message='パスワードを入力してください'), 
                                     Length(min=6, message='6文字以上で入力してください')])
    confirm_password = PasswordField('パスワード（確認）', 
                                   validators=[DataRequired(message='確認用パスワードを入力してください'), 
                                             EqualTo('password', message='パスワードが一致しません')])
    submit = SubmitField('登録')
    
    def validate_username(self, username):
        session = Session()
        try:
            user = session.query(User).filter_by(username=username.data).first()
            if user:
                raise ValidationError('このユーザー名は既に使用されています')
        finally:
            session.close()
    
    def validate_email(self, email):
        session = Session()
        try:
            user = session.query(User).filter_by(email=email.data).first()
            if user:
                raise ValidationError('このメールアドレスは既に登録されています')
        finally:
            session.close()

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', 
                       validators=[DataRequired(message='メールアドレスを入力してください'), 
                                 Email(message='有効なメールアドレスを入力してください')])
    password = PasswordField('パスワード', 
                           validators=[DataRequired(message='パスワードを入力してください')])
    remember = BooleanField('ログイン状態を保持')
    submit = SubmitField('ログイン')