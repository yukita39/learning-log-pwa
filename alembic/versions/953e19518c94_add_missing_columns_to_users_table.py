"""Add missing columns to users table

Revision ID: 953e19518c94
Revises: f602f6c194d5
Create Date: 2025-06-29 13:41:12.948245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '953e19518c94'
down_revision: Union[str, Sequence[str], None] = 'f602f6c194d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # usersテーブルに不足しているカラムを追加
    op.add_column('users', sa.Column('username', sa.String(80), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # デフォルト値を設定
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    
    # usernameにユニーク制約を追加（オプション）
    # op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'username')
