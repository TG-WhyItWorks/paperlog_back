"""baseline after purge

Revision ID: 008903488727
Revises: 
Create Date: 2025-08-09 17:29:37.110850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008903488727'
down_revision = None   # 꼭 None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
