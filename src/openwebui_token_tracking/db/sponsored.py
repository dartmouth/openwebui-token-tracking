import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


class SponsoredAllowanceBaseModels(Base):
    """SQLAlchemy model for the sponsored allowance base models association table

    Junction table that defines which base models are available under a specific
    sponsored allowance.
    """

    __tablename__ = "token_tracking_sponsored_allowance_base_models"
    sponsored_allowance_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_sponsored_allowance.id"),
        primary_key=True,
    )
    """Part of composite primary key, references :attr:`SponsoredAllowance.id`"""
    base_model_id = sa.Column(
        sa.String(length=255),
        sa.ForeignKey("token_tracking_model_pricing.id"),
        primary_key=True,
    )
    """Part of composite primary key, references :attr:`ModelPricing.id`"""
    sponsored_allowance = relationship(
        "SponsoredAllowance", back_populates="base_models"
    )
    """Relationship with the :class:`SponsoredAllowance` model, linked via :attr:`SponsoredAllowance.base_models`"""
    base_model = relationship("ModelPricing")
    """Relationship with the :class:`ModelPricing` model"""


class SponsoredAllowance(Base):
    """SQLAlchemy model for the sponsored allowance table

    Represents a credit allowance sponsored by an entity, which can be used by users
    to access specific AI models without consuming their personal credits.
    """

    __tablename__ = "token_tracking_sponsored_allowance"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    """Primary key UUID for the sponsored allowance"""
    creation_date = sa.Column(
        sa.DateTime(timezone=True),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    """Timestamp when the sponsored allowance was created"""
    name = sa.Column(sa.String(length=255))
    """Unique name of the sponsored allowance"""
    sponsor_id = sa.Column(sa.String(length=255))
    """Identifier for the entity sponsoring this allowance"""
    base_models = relationship(
        "SponsoredAllowanceBaseModels", back_populates="sponsored_allowance"
    )
    """Relationship with the :class:`SponsoredAllowanceBaseModels` model, linked via :attr:`SponsoredAllowanceBaseModels.sponsored_allowance`"""
    total_credit_limit = sa.Column(sa.Integer, nullable=False)
    """Total credit limit across all users and base models, i.e., maximum sponsored amount"""
    daily_credit_limit = sa.Column(sa.Integer, nullable=True)
    """Daily credit limit per user"""
