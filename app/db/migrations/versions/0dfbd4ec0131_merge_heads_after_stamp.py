"""Merge heads after stamp

Revision ID: 0dfbd4ec0131
Revises: 59c46fb8d711, c57665ebfb23
Create Date: 2025-08-07 20:19:53.228409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dfbd4ec0131'
down_revision: Union[str, Sequence[str], None] = ('59c46fb8d711', 'c57665ebfb23')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
