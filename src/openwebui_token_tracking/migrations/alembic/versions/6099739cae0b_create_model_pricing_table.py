"""create_model_pricing_table

Revision ID: 6099739cae0b
Revises: 99fb3ad5e0e7
Create Date: 2025-01-30 12:56:00.559456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6099739cae0b"
down_revision: Union[str, None] = "99fb3ad5e0e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_tracking_model_pricing",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column("provider", sa.String(length=255)),
        sa.Column("name", sa.String(length=255)),
        sa.Column("input_cost_credits", sa.Integer()),
        sa.Column("per_input_tokens", sa.Integer()),
        sa.Column("output_cost_credits", sa.Integer()),
        sa.Column("per_output_tokens", sa.Integer()),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_tracking_model_pricing")
