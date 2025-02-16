"""create_base_settings_table

Revision ID: 036cd1c4af2d
Revises: c46ceb8649c3
Create Date: 2025-02-11 11:45:34.221772

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "036cd1c4af2d"
down_revision: Union[str, None] = "c46ceb8649c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_tracking_base_settings",
        sa.Column("setting_key", sa.String(length=255), primary_key=True),
        sa.Column("setting_value", sa.String(length=255)),
        sa.Column("description", sa.String(length=255)),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_tracking_base_settings")
