# forms.py - パスワードポリシーを強化したバージョン

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from db import Session, User
import re

# カスタムバリデーター
def password_complexity(form, field):
    """パスワードの複雑性をチェックするカスタムバリデーター"""
    password = field.data
    
    # 基本的な長さチェック（他のバリデーターでも行うが、ここでも確認）
    if len(password) < 8:
        raise ValidationError('パスワードは8文字以上で入力してください。')
    
    # 複雑性チェック
    checks = {
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'digit': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    
    # 必須要件：英字（大文字小文字どちらか）と数字
    if not ((checks['uppercase'] or checks['lowercase']) and checks['digit']):
        raise ValidationError('パスワードは英字と数字を両方含める必要があります。')
    
    # 推奨要件のカウント（4つのうち3つ以上を満たす）
    satisfied_count = sum(checks.values())
    if satisfied_count < 3:
        missing = []
        if not checks['uppercase']:
            missing.append('大文字')
        if not checks['lowercase']:
            missing.append('小文字')
        if not checks['digit']:
            missing.append('数字')
        if not checks['special']:
            missing.append('特殊文字(!@#$%など)')
        
        raise ValidationError(
            f'より安全なパスワードにするため、以下のうち少なくとも3種類を含めてください: '
            f'大文字、小文字、数字、特殊文字。現在不足: {", ".join(missing[:2])}'
        )

def common_password_check(form, field):
    """よくある脆弱なパスワードをチェック"""
    password = field.data.lower()
    
    # よくある脆弱なパスワードのリスト（実際はもっと大きなリストを使用）
    common_passwords = [
        'password', 'password123', 'admin', 'qwerty', '123456', 
        '12345678', 'abc123', 'welcome', 'letmein', 'monkey',
        'dragon', 'football', 'iloveyou', 'master', 'hello',
        'freedom', 'whatever', 'shadow', 'sunshine', 'chocolate'
    ]
    
    if password in common_passwords:
        raise ValidationError('このパスワードは一般的すぎて安全ではありません。別のパスワードを選んでください。')
    
    # ユーザー名やメールアドレスの一部を含んでいないかチェック
    if hasattr(form, 'username') and form.username.data:
        if form.username.data.lower() in password:
            raise ValidationError('パスワードにユーザー名を含めることはできません。')
    
    if hasattr(form, 'email') and form.email.data:
        email_local = form.email.data.split('@')[0].lower()
        if len(email_local) > 3 and email_local in password:
            raise ValidationError('パスワードにメールアドレスの一部を含めることはできません。')

class RegistrationForm(FlaskForm):
    """ユーザー登録フォーム（強化版）"""
    email = StringField('メールアドレス', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Email(message='有効なメールアドレスを入力してください')
    ])
    
    username = StringField('ユーザー名', validators=[
        DataRequired(message='ユーザー名を入力してください'),
        Length(min=3, max=20, message='ユーザー名は3文字以上20文字以下で入力してください'),
        Regexp('^[A-Za-z0-9_]+$', message='ユーザー名は英数字とアンダースコアのみ使用できます')
    ])
    
    password = PasswordField('パスワード', validators=[
        DataRequired(message='パスワードを入力してください'),
        Length(min=8, max=128, message='パスワードは8文字以上128文字以下で入力してください'),
        password_complexity,  # カスタムバリデーター
        common_password_check  # 脆弱パスワードチェック
    ])
    
    password_confirm = PasswordField('パスワード（確認）', validators=[
        DataRequired(message='確認用パスワードを入力してください'),
        EqualTo('password', message='パスワードが一致しません')
    ])
    
    submit = SubmitField('登録')
    
    def validate_email(self, email):
        """メールアドレスの重複チェック"""
        with Session() as session:
            user = session.query(User).filter_by(email=email.data).first()
            if user:
                raise ValidationError('このメールアドレスは既に登録されています')
    
    def validate_username(self, username):
        """ユーザー名の重複チェック"""
        with Session() as session:
            user = session.query(User).filter_by(username=username.data).first()
            if user:
                raise ValidationError('このユーザー名は既に使用されています')

class LoginForm(FlaskForm):
    """ログインフォーム"""
    email = StringField('メールアドレス', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Email(message='有効なメールアドレスを入力してください')
    ])
    
    password = PasswordField('パスワード', validators=[
        DataRequired(message='パスワードを入力してください')
    ])
    
    remember = BooleanField('ログイン状態を保持')
    submit = SubmitField('ログイン')

class ChangePasswordForm(FlaskForm):
    """パスワード変更フォーム（将来の実装用）"""
    current_password = PasswordField('現在のパスワード', validators=[
        DataRequired(message='現在のパスワードを入力してください')
    ])
    
    new_password = PasswordField('新しいパスワード', validators=[
        DataRequired(message='新しいパスワードを入力してください'),
        Length(min=8, max=128, message='パスワードは8文字以上128文字以下で入力してください'),
        password_complexity,
        common_password_check
    ])
    
    new_password_confirm = PasswordField('新しいパスワード（確認）', validators=[
        DataRequired(message='確認用パスワードを入力してください'),
        EqualTo('new_password', message='パスワードが一致しません')
    ])
    
    submit = SubmitField('パスワードを変更')
    
    def validate_new_password(self, field):
        """現在のパスワードと同じでないことを確認"""
        if self.current_password.data == field.data:
            raise ValidationError('新しいパスワードは現在のパスワードと異なるものにしてください。')