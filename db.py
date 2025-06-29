# db.py - PostgreSQL対応版
import os
from datetime import datetime
from sqlalchemy import create_engine, Date, Time, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=True)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    calendar_id = Column(String(255), nullable=True)

    # User が持つ Log のリスト
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)
    content = Column(Text)
    impression = Column(Text)
    tags = Column(Text, default="")

    # どのユーザーのログかを紐づける外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 逆引き
    user = relationship("User", back_populates="logs")


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