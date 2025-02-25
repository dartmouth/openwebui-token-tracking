"""create_credit_group_table

Revision ID: c46ceb8649c3
Revises: 6099739cae0b
Create Date: 2025-01-31 07:06:51.722238

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c46ceb8649c3"
down_revision: Union[str, None] = "6099739cae0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_tracking_credit_group",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255)),
        sa.Column("max_credit", sa.Integer()),
        sa.Column("description", sa.String(length=255)),
        if_not_exists=True,
    )
    op.create_table(
        "token_tracking_credit_group_user",
        sa.Column(
            "credit_group_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("token_tracking_credit_group.id"),
        ),
        sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id")),
        if_not_exists=True,
    )

    op.create_index(
        "idx_token_tracking_credit_group_name_lower",
        "token_tracking_credit_group",
        [sa.text("lower(name)")],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_tracking_credit_group_users")
    op.drop_table("token_tracking_credit_group")
