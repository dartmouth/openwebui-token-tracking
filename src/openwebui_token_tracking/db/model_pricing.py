import sqlalchemy as sa

from .base import Base


class ModelPricing(Base):
    """SQLAlchemy model for the model pricing table

    Stores pricing information for AI models, including credit costs for input and output tokens.
    """

    __tablename__ = "token_tracking_model_pricing"
    provider = sa.Column(sa.String(length=255), primary_key=True)
    """Provider of the AI model (e.g., 'openai', 'anthropic'), part of the composite primary key"""
    id = sa.Column(sa.String(length=255), primary_key=True)
    """Identifier of the model (e.g., 'gpt-4', 'claude-3'), part of the composite primary key"""
    name = sa.Column(sa.String(length=255))
    """Display name of the model"""
    input_cost_credits = sa.Column(sa.Integer())
    """Number of credits charged for input tokens"""
    per_input_tokens = sa.Column(sa.Integer())
    """Number of input tokens per credit charge (e.g., 1000000 tokens per `input_cost_credits`)"""
    output_cost_credits = sa.Column(sa.Integer())
    """Number of credits charged for output tokens"""
    per_output_tokens = sa.Column(sa.Integer())
    """Number of output tokens per credit charge (e.g., 1000000 tokens per `output_cost_credits`)"""
