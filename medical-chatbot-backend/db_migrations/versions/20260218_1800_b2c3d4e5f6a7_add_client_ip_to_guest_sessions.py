"""add client_ip to guest_sessions

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-18 18:00:00.000000

Adds client_ip column to guest_sessions table for IP-based fingerprinting
to prevent the "clear cookies" loophole.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'guest_sessions',
        sa.Column('client_ip', sa.String(), nullable=True)
    )
    # Add index for fast IP lookups
    op.create_index(
        'ix_guest_sessions_client_ip',
        'guest_sessions',
        ['client_ip'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_guest_sessions_client_ip', table_name='guest_sessions')
    op.drop_column('guest_sessions', 'client_ip')
