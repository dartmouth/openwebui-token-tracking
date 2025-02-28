import sqlalchemy as sa

from .base import Base


class TokenUsageLog(Base):
    """SQLAlchemy model for the token usage log table

    Records individual token usage events for tracking and billing purposes.
    Each record represents a single API call with token consumption details.
    """

    __tablename__ = "token_tracking_usage_log"
    log_date = sa.Column(
        "log_date",
        sa.DateTime(timezone=True),
        primary_key=True,
    )
    """Timestamp when the token usage occurred, part of the composite primary key"""
    user_id = sa.Column(sa.String(length=255), primary_key=True)
    """ID of the user who consumed the tokens, part of the composite primary key"""
    provider = sa.Column(sa.String(length=255), primary_key=True)
    """Provider of the AI model (e.g., 'openai', 'anthropic'), part of the composite primary key"""
    model_id = sa.Column(sa.String(length=255), primary_key=True)
    """ID of the model used (e.g., 'gpt-4', 'claude-3'), part of the composite primary key"""
    sponsored_allowance_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_sponsored_allowance.id"),
        nullable=True,
    )
    """Optional reference to a :class:`SponsoredAllowance` if the usage was covered by a sponsor"""
    prompt_tokens = sa.Column(sa.Integer())
    """Number of tokens used in the input/prompt"""
    response_tokens = sa.Column(sa.Integer())
    """Number of tokens generated in the output/response"""
