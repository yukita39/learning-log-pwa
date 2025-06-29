# alembic/env.py - PostgreSQL対応版

from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))

# あなたのモデルをインポート
from db import Base, DATABASE_URL

# this is the Alembic Config object
config = context.config

# Alembicの設定にDATABASE_URLを設定
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# モデルのメタデータを設定
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  # 型の変更を検出
            compare_server_default=True,  # デフォルト値の変更を検出
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()