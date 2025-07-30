"""merge diverged heads

Revision ID: 8679439c1d74
Revises: be253ea4e8a5, ab6b9311c502
Create Date: 2025-07-29 20:59:27.364324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8679439c1d74'
down_revision: Union[str, Sequence[str], None] = ('be253ea4e8a5', 'ab6b9311c502')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
