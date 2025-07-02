"""merge password features with existing migration

Revision ID: dad4fa4c5a89
Revises: 953e19518c94, add_password_features
Create Date: 2025-07-02 13:04:13.985911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dad4fa4c5a89'
down_revision: Union[str, Sequence[str], None] = ('953e19518c94', 'add_password_features')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
