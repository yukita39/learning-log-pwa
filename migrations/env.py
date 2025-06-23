# migrations/env.py

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# あなたの MetaData をインポート
from db import Base

# Alembic Config オブジェクト
config = context.config

# logging をセットアップ
fileConfig(config.config_file_name)

# target_metadata を指定
target_metadata = Base.metadata

# 環境変数か ini のデフォルトを選ぶ
db_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    """オフラインモード（SQL だけ出力）"""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """オンラインモード（実際に DB に接続）"""
    connectable = engine_from_config(
        {"sqlalchemy.url": db_url},  # ここで確実に文字列を渡す
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

