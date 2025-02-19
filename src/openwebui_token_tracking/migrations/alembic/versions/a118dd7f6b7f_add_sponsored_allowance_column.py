"""add sponsored allowance column

Revision ID: a118dd7f6b7f
Revises: 10d29ec2fd0a
Create Date: 2025-02-19 13:16:21.441366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a118dd7f6b7f"
down_revision: Union[str, None] = "10d29ec2fd0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    conn = op.get_bind()
    insp = sa.inspect(conn)
    columns = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if column_exists("token_tracking_usage_log", "sponsored_allowance_id"):
        return
    with op.batch_alter_table("token_tracking_usage_log") as batch_op:
        batch_op.add_column(
            sa.Column(
                "sponsored_allowance_id",
                sa.UUID(as_uuid=True),
                sa.ForeignKey(
                    "token_tracking_sponsored_allowance.id",
                    name="fk_usage_log_sponsored_allowance",
                ),
                nullable=True,
            ),
        )


def downgrade() -> None:
    with op.batch_alter_table("token_tracking_token_usage_log") as batch_op:
        batch_op.drop_column("sponsored_allowance_id")
