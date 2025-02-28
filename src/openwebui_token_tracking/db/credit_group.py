import uuid

from sqlalchemy.orm import relationship
import sqlalchemy as sa

from .base import Base


class CreditGroupUser(Base):
    """SQLAlchemy model for the credit group user table"""

    __tablename__ = "token_tracking_credit_group_user"
    credit_group_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_credit_group.id"),
        primary_key=True,
    )
    """ID of the credit group, references :attr:`CreditGroup.id`"""
    user_id = sa.Column(
        sa.String(length=255), sa.ForeignKey("user.id"), primary_key=True
    )
    """ID of a member of the credit group, references :attr:`User.id`"""

    credit_group = relationship("CreditGroup", back_populates="users")
    """Relationship with the :class:`CreditGroup`, linked via :attr:`CreditGroup.users`"""
    user = relationship("User", back_populates="credit_groups")
    """Relationship with the :class:`User` model,  linked via :attr:`User.credit_groups`"""


class CreditGroup(Base):
    """SQLAlchemy model for the credit group table"""

    __tablename__ = "token_tracking_credit_group"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    """Primary key UUID for the credit group"""
    name = sa.Column(sa.String(length=255))
    """Name of the credit group, must be unique (case-insensitive)"""
    max_credit = sa.Column(sa.Integer())
    """Maximum number of credits allocated to members of this group"""
    description = sa.Column(sa.String(length=255))
    """Description of the credit group's purpose or members"""
    users = relationship("CreditGroupUser", back_populates="credit_group")
    """Relationship with the :class:`CreditGroupUser` model, linked via :attr:`CreditGroupUser.credit_group`"""
    __table_args__ = (
        sa.Index(
            "idx_token_tracking_credit_group_name_lower",
            sa.func.lower(name),
            unique=True,
        ),
    )
    """Table arguments including a case-insensitive unique index on the :attr:`name` column"""
