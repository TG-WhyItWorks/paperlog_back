"""merge heads after purge

Revision ID: af72ec06cf06
Revises: 008903488727, 37fb65d0e141
Create Date: 2025-08-09 19:59:56.077072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af72ec06cf06'
down_revision: Union[str, Sequence[str], None] = ('008903488727', '37fb65d0e141')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
