import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ① ここで Base.metadata を import
from db import Base

# -------------------------------------------------
# Alembic Config オブジェクト
# -------------------------------------------------
config = context.config
fileConfig(config.config_file_name)

# ② metadata を設定（`--autogenerate` の対象）
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline: SQL スクリプト出力のみ"""
    url = os.getenv("DATABASE_URL", "sqlite:///learning.db")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online: 実際に DB へ接続して適用"""
    # ③ ini セクションを dict で取得して書き換える
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv(
        "DATABASE_URL", "sqlite:///learning.db"
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------
# エントリポイント
# -------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
