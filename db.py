# db.py - PostgreSQL対応版
from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
import os
from dotenv import load_dotenv

# .envファイルを読み込み（ローカル開発用）
load_dotenv()

# ── 接続文字列 ───────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",                # Renderの環境変数から取得
    "sqlite:///learning.db"        # ローカル開発時のフォールバック
)

# RenderのPostgreSQLは古い形式のURLを使うことがあるので修正
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# ────────────────────────────────────────────

# エンジンの作成（PostgreSQL用の設定を追加）
engine = create_engine(
    DATABASE_URL, 
    future=True, 
    echo=False,
    # PostgreSQL用の追加設定
    pool_pre_ping=True,  # 接続の健全性をチェック
    pool_recycle=300,    # 5分ごとに接続をリサイクル
)

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# PasswordHistoryとPasswordResetTokenをUserクラスより前に定義
class PasswordHistory(Base):
    __tablename__ = 'password_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション（back_populatesは後で設定）

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    
    # リレーション（back_populatesは後で設定）
    
    @classmethod
    def create_token(cls, user_id, expires_in_hours=1):
        """パスワードリセット用のトークンを生成"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """トークンが有効かチェック"""
        return not self.used and datetime.utcnow() < self.expires_at

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    calendar_id = Column(String(255), nullable=True)
    
    # 追加フィールド
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)

    # リレーション
    logs = relationship('Log', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    password_history = relationship('PasswordHistory', back_populates='user', 
                                  order_by='PasswordHistory.created_at.desc()', 
                                  cascade='all, delete-orphan')
    reset_tokens = relationship('PasswordResetToken', back_populates='user', 
                              cascade='all, delete-orphan')
    
    def set_password(self, password):
        """パスワードを設定"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def check_password_history(self, password, history_count=5):
        """過去のパスワードと照合（デフォルトは過去5回分）"""
        # 現在のパスワードをチェック
        if self.check_password(password):
            return True
        
        # 過去のパスワードをチェック
        for history in self.password_history[:history_count]:
            if check_password_hash(history.password_hash, password):
                return True
        
        return False
    
    def is_locked(self):
        """アカウントがロックされているかチェック"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def increment_failed_attempts(self):
        """ログイン失敗回数を増加"""
        self.failed_login_attempts += 1
        # 5回失敗したら30分間ロック
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_attempts(self):
        """ログイン成功時に失敗回数をリセット"""
        self.failed_login_attempts = 0
        self.locked_until = None

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)
    content = Column(Text)
    impression = Column(Text)
    tags = Column(Text, default="")

    # 外部キーにondelete='CASCADE'を追加
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    # リレーション
    user = relationship("User", back_populates="logs")

# リレーションのback_populatesを設定
PasswordHistory.user = relationship('User', back_populates='password_history')
PasswordResetToken.user = relationship('User', back_populates='reset_tokens')

# 開発用: 直接実行してテーブルを生成
if __name__ == "__main__":
    # 既存のテーブル情報を表示
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"Existing tables: {existing_tables}")
    
    if existing_tables:
        print("\nTable details:")
        for table in existing_tables:
            print(f"\n{table}:")
            for column in inspector.get_columns(table):
                print(f"  - {column['name']}: {column['type']}")
    
    # テーブルを作成
    print("\nCreating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")