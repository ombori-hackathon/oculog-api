"""add unique constraint on user_id and log_date

Revision ID: c1f2a3b4c5d6
Revises: 82120bd6be61
Create Date: 2026-01-29 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c1f2a3b4c5d6'
down_revision: Union[str, None] = '82120bd6be61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_condition_logs_user_date',
        'condition_logs',
        ['user_id', 'log_date']
    )


def downgrade() -> None:
    op.drop_constraint('uq_condition_logs_user_date', 'condition_logs', type_='unique')
