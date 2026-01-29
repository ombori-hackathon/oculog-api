"""replace items with eye tracking schema

Revision ID: 0c5aaf492ee3
Revises: 84c20da21d5d
Create Date: 2026-01-29 12:16:37.267330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c5aaf492ee3'
down_revision: Union[str, None] = '84c20da21d5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fixed UUID for seeded user (for consistency across environments)
KAMIL_USER_ID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create users table
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('login', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('timezone', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login')
    )

    # Create condition_logs table
    op.create_table('condition_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('log_date', sa.Date(), nullable=False),
    sa.Column('period_end_date', sa.Date(), nullable=True),
    sa.Column('overall_rating', sa.Integer(), nullable=True),
    sa.Column('burning', sa.Integer(), nullable=True),
    sa.Column('redness', sa.Integer(), nullable=True),
    sa.Column('itching', sa.Integer(), nullable=True),
    sa.Column('tearing', sa.Integer(), nullable=True),
    sa.Column('swelling', sa.Integer(), nullable=True),
    sa.Column('screen_time_hours', sa.Float(), nullable=True),
    sa.Column('sleep_hours', sa.Float(), nullable=True),
    sa.Column('sleep_quality', sa.Integer(), nullable=True),
    sa.Column('water_intake_liters', sa.Float(), nullable=True),
    sa.Column('caffeine_cups', sa.Integer(), nullable=True),
    sa.Column('alcohol_units', sa.Integer(), nullable=True),
    sa.Column('stress_level', sa.Integer(), nullable=True),
    sa.Column('outdoor_hours', sa.Float(), nullable=True),
    sa.Column('used_artificial_tears', sa.Boolean(), nullable=True),
    sa.Column('used_warm_compress', sa.Boolean(), nullable=True),
    sa.Column('used_lid_scrub', sa.Boolean(), nullable=True),
    sa.Column('used_prescription_drops', sa.Boolean(), nullable=True),
    sa.Column('used_omega3', sa.Boolean(), nullable=True),
    sa.Column('used_humidifier', sa.Boolean(), nullable=True),
    sa.Column('wore_contacts', sa.Boolean(), nullable=True),
    sa.Column('ac_exposure', sa.Boolean(), nullable=True),
    sa.Column('heating_exposure', sa.Boolean(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('treatments_notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create weather_data table
    op.create_table('weather_data',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('condition_log_id', sa.UUID(), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('location_name', sa.String(length=255), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('temperature_c', sa.Float(), nullable=True),
    sa.Column('humidity_percent', sa.Integer(), nullable=True),
    sa.Column('pressure_hpa', sa.Float(), nullable=True),
    sa.Column('wind_speed_kmh', sa.Float(), nullable=True),
    sa.Column('conditions', sa.String(length=100), nullable=True),
    sa.Column('air_quality_index', sa.Integer(), nullable=True),
    sa.Column('uv_index', sa.Float(), nullable=True),
    sa.Column('pollen_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['condition_log_id'], ['condition_logs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('condition_log_id')
    )

    # Drop old items table
    op.drop_table('items')

    # Seed kamil user
    op.execute(f"""
        INSERT INTO users (id, login, timezone)
        VALUES ('{KAMIL_USER_ID}', 'kamil', 'Europe/Warsaw')
    """)


def downgrade() -> None:
    # Remove seeded user
    op.execute(f"DELETE FROM users WHERE id = '{KAMIL_USER_ID}'")

    # Recreate items table
    op.create_table('items',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('items_pkey'))
    )

    # Drop new tables
    op.drop_table('weather_data')
    op.drop_table('condition_logs')
    op.drop_table('users')

    # Note: We don't drop the uuid-ossp extension as other things might use it
