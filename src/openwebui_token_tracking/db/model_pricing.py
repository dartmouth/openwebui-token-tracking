import sqlalchemy as sa

from .base import Base


class ModelPricing(Base):
    """SQLAlchemy model for the model pricing table"""

    __tablename__ = "token_tracking_model_pricing"
    provider = sa.Column(sa.String(length=255), primary_key=True)
    id = sa.Column(sa.String(length=255), primary_key=True)
    name = sa.Column(sa.String(length=255))
    input_cost_credits = sa.Column(sa.Integer())
    per_input_tokens = sa.Column(sa.Integer())
    output_cost_credits = sa.Column(sa.Integer())
    per_output_tokens = sa.Column(sa.Integer())
