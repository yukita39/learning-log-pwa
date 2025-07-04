"""last_log

Revision ID: f541dd128ff8
Revises: dad4fa4c5a89
Create Date: 2025-07-04 21:27:53.859651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'f541dd128ff8'
down_revision: Union[str, Sequence[str], None] = 'dad4fa4c5a89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 接続を取得して既存のカラムをチェック
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # last_loginカラムが存在しない場合のみ追加
    if 'last_login' not in columns:
        op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
        print("✅ last_loginカラムを追加しました")
    else:
        print("ℹ️ last_loginカラムは既に存在します - スキップ")
    
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('logs_user_id_fkey'), 'logs', type_='foreignkey')
    op.create_foreign_key(None, 'logs', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_password_history_user_id'), table_name='password_history')
    op.drop_constraint(op.f('password_history_user_id_fkey'), 'password_history', type_='foreignkey')
    op.create_foreign_key(None, 'password_history', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_constraint(op.f('password_reset_tokens_user_id_fkey'), 'password_reset_tokens', type_='foreignkey')
    op.create_foreign_key(None, 'password_reset_tokens', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)
    op.alter_column('users', 'password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('users', 'failed_login_attempts',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('users', 'is_admin',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=True)
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # カラムの存在をチェック
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # last_loginカラムが存在する場合のみ削除
    if 'last_login' in columns:
        op.drop_column('users', 'last_login')
    
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.alter_column('users', 'is_admin',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=True)
    op.alter_column('users', 'failed_login_attempts',
               existing_type=sa.INTEGER(),
               server_default=sa.text('0'),
               existing_nullable=True)
    op.alter_column('users', 'password_hash',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=128),
               existing_nullable=False)
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)
    op.drop_constraint(None, 'password_reset_tokens', type_='foreignkey')
    op.create_foreign_key(op.f('password_reset_tokens_user_id_fkey'), 'password_reset_tokens', 'users', ['user_id'], ['id'])
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)
    op.drop_constraint(None, 'password_history', type_='foreignkey')
    op.create_foreign_key(op.f('password_history_user_id_fkey'), 'password_history', 'users', ['user_id'], ['id'])
    op.create_index(op.f('ix_password_history_user_id'), 'password_history', ['user_id'], unique=False)
    op.drop_constraint(None, 'logs', type_='foreignkey')
    op.create_foreign_key(op.f('logs_user_id_fkey'), 'logs', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###