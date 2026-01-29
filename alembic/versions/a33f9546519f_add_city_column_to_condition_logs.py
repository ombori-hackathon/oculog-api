"""Add city column to condition_logs

Revision ID: a33f9546519f
Revises: 5cd38de5712f
Create Date: 2026-01-29 14:04:14.042057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a33f9546519f'
down_revision: Union[str, None] = '5cd38de5712f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Column may already exist (added manually), so just update existing rows and make non-nullable
    # Set default for existing rows
    op.execute("UPDATE condition_logs SET city = 'Unknown' WHERE city IS NULL")
    # Make non-nullable
    op.alter_column('condition_logs', 'city', nullable=False)


def downgrade() -> None:
    op.drop_column('condition_logs', 'city')
