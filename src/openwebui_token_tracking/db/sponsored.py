import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


class SponsoredAllowanceBaseModels(Base):
    """SQLAlchemy model for the sponsored allowance base models association table"""

    __tablename__ = "token_tracking_sponsored_allowance_base_models"
    sponsored_allowance_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_sponsored_allowance.id"),
        primary_key=True,
    )
    base_model_id = sa.Column(
        sa.String(length=255),
        sa.ForeignKey("token_tracking_model_pricing.id"),
        primary_key=True,
    )
    sponsored_allowance = relationship(
        "SponsoredAllowance", back_populates="base_models"
    )
    base_model = relationship("ModelPricing")


class SponsoredAllowance(Base):
    """SQLAlchemy model for the sponsored allowance table"""

    __tablename__ = "token_tracking_sponsored_allowance"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    creation_date = sa.Column(
        sa.DateTime(timezone=True),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    name = sa.Column(sa.String(length=255))
    sponsor_id = sa.Column(sa.String(length=255))
    base_models = relationship(
        "SponsoredAllowanceBaseModels", back_populates="sponsored_allowance"
    )
    total_credit_limit = sa.Column(sa.Integer, nullable=False)
    """Total credit limit across all users and base models, i.e., maximum sponsored amount"""
    daily_credit_limit = sa.Column(sa.Integer, nullable=True)
    """Daily credit limit per user"""
