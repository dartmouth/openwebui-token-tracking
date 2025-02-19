"""create sponsored allowance table

Revision ID: 10d29ec2fd0a
Revises: 036cd1c4af2d
Create Date: 2025-02-19 13:12:28.790144

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "10d29ec2fd0a"
down_revision: Union[str, None] = "036cd1c4af2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_tracking_sponsored_allowance",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255)),
        sa.Column("sponsor_id", sa.String(length=255)),
        sa.Column("total_credit_limit", sa.Integer(), nullable=False),
        sa.Column("daily_credit_limit", sa.Integer(), nullable=True),
        if_not_exists=True,
    )
    op.create_table(
        "token_tracking_sponsored_allowance_base_models",
        sa.Column(
            "sponsored_allowance_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("token_tracking_sponsored_allowance.id"),
        ),
        sa.Column(
            "base_model_id",
            sa.String(length=255),
            sa.ForeignKey("token_tracking_model_pricing.id"),
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_tracking_sponsored_allowance_base_models")
    op.drop_table("token_tracking_sponsored_allowance")
