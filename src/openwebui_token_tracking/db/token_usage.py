import sqlalchemy as sa

from .base import Base


class TokenUsageLog(Base):
    """SQLAlchemy model for the token usage log table"""

    __tablename__ = "token_tracking_usage_log"
    log_date = sa.Column(
        "log_date",
        sa.DateTime(timezone=True),
        primary_key=True,
    )
    user_id = sa.Column(sa.String(length=255), primary_key=True)
    provider = sa.Column(sa.String(length=255), primary_key=True)
    model_id = sa.Column(sa.String(length=255), primary_key=True)
    sponsored_allowance_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_sponsored_allowance.id"),
        nullable=True,
    )
    prompt_tokens = sa.Column(sa.Integer())
    response_tokens = sa.Column(sa.Integer())
