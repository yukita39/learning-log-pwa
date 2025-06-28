# db.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Date, Time, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# ── 接続文字列 ───────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",                # 本番 Render ではここに Postgres URL
    "sqlite:///learning.db"        # 未設定時はローカル SQLite
)
# ────────────────────────────────────────────

engine = create_engine(DATABASE_URL, future=True, echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=True)  # オプション
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


# 開発用: 初回だけ実行してテーブルを生成
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")