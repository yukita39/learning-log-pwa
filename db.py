# db.py
import os
from sqlalchemy import create_engine, Column, Integer, Text, Date, Time
from sqlalchemy.orm import declarative_base, sessionmaker

# ── 接続文字列 ───────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",                # 本番 Render ではここに Postgres URL
    "sqlite:///learning.db"        # 未設定時はローカル SQLite
)
# ────────────────────────────────────────────

engine = create_engine(DATABASE_URL, future=True, echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# テーブル定義
class Log(Base):
    __tablename__ = "logs"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    duration   = Column(Integer, nullable=False)
    content    = Column(Text)
    impression = Column(Text)
    tags       = Column(Text, default="")          # NEW! カンマ区切り

# 開発用: 初回だけ実行してテーブルを生成
if __name__ == "__main__":
    Base.metadata.create_all(engine)