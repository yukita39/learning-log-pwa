"""add user table and calendar_id

Revision ID: ed083093e5fb
Revises: ebf99da6f82c
Create Date: 2025-06-27 10:31:10.937006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed083093e5fb'
down_revision: Union[str, Sequence[str], None] = 'ebf99da6f82c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) user テーブルを作る
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(128), nullable=False),
        sa.Column('calendar_id', sa.String(), nullable=True),
    )
    # 2) （必要なら）logs テーブルに user_id カラムを追加
    op.add_column('logs',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_logs_user', 'logs', 'user', ['user_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_logs_user', 'logs', type_='foreignkey')
    op.drop_column('logs', 'user_id')
    op.drop_table('user')
