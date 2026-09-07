"""merge phishing and ioc heads

Revision ID: 4c2ccc49af16
Revises: 042fb422f857, 27aaffe440ce
Create Date: 2026-09-07 18:56:10.022826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2ccc49af16'
down_revision: Union[str, Sequence[str], None] = ('042fb422f857', '27aaffe440ce')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
