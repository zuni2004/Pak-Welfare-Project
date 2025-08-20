"""add nicop enum values to document_type_enum

Revision ID: c8a0f5a1783e
Revises: 0033fcacf690
Create Date: 2025-08-20 14:22:54.772881

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8a0f5a1783e"
down_revision: Union[str, None] = "0033fcacf690"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing enum values to document_type_enum
    op.execute("ALTER TYPE document_type_enum ADD VALUE IF NOT EXISTS 'NICOP_FRONT'")
    op.execute("ALTER TYPE document_type_enum ADD VALUE IF NOT EXISTS 'NICOP_BACK'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values easily
    # You would need to recreate the enum type if rollback is needed
    pass
