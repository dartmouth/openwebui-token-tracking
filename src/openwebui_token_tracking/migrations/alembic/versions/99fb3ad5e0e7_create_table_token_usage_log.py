"""create_table_token_usage_log
Revision ID: 99fb3ad5e0e7
Revises:
Create Date: 2024-01-30 12:51:01.998946
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "99fb3ad5e0e7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ("token_tracking",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_tracking_usage_log",
        sa.Column("log_date", sa.DateTime(timezone=True)),
        sa.Column("user_id", sa.String(length=255)),
        sa.Column("provider", sa.String(length=255)),
        sa.Column("model_id", sa.String(length=255)),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("response_tokens", sa.Integer()),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_tracking_usage_log")
