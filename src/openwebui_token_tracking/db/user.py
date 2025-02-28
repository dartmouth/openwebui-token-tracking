from sqlalchemy.orm import relationship
import sqlalchemy as sa

from .base import Base


class User(Base):
    """SQLAlchemy model for the user table.

    Mocks (parts of) the user table managed by Open WebUI
    and is only used for testing purposes.

    This model represents users who can consume tokens and be part of credit groups.
    In production, this would be replaced by the actual user model from Open WebUI.
    """

    __tablename__ = "user"
    id = sa.Column(sa.String(length=255), primary_key=True)
    """Primary key identifier for the user"""
    name = sa.Column(sa.String(length=255))
    """User's display name"""
    email = sa.Column(sa.String(length=255))
    """User's email address"""

    credit_groups = relationship("CreditGroupUser", back_populates="user")
    """Relationship with the :class:`CreditGroupUser` model, linked via :attr:`CreditGroupUser.user`"""
