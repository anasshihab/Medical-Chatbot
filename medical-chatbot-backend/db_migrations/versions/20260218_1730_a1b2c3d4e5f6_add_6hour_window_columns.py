"""add 6-hour window columns to users and guest_sessions

Revision ID: a1b2c3d4e5f6
Revises: 75e586590fd1
Create Date: 2026-02-18 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '75e586590fd1'
branch_labels = None
depends_on = None

# Sentinel timestamp used as the default for existing rows
_EPOCH = datetime(2000, 1, 1, 0, 0, 0)


def upgrade() -> None:
    # ── users table ────────────────────────────────────────────────────────────
    op.add_column(
        'users',
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='0')
    )
    op.add_column(
        'users',
        sa.Column(
            'last_reset_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("'2000-01-01 00:00:00'")
        )
    )

    # Also update the plantype enum to include GUEST value
    # SQLite doesn't enforce enums so this is a no-op for SQLite;
    # for PostgreSQL we need to add the new enum value.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TYPE plantype ADD VALUE IF NOT EXISTS 'GUEST'")

    # ── guest_sessions table ───────────────────────────────────────────────────
    op.add_column(
        'guest_sessions',
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='0')
    )
    op.add_column(
        'guest_sessions',
        sa.Column(
            'last_reset_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("'2000-01-01 00:00:00'")
        )
    )


def downgrade() -> None:
    op.drop_column('guest_sessions', 'last_reset_at')
    op.drop_column('guest_sessions', 'question_count')
    op.drop_column('users', 'last_reset_at')
    op.drop_column('users', 'question_count')
