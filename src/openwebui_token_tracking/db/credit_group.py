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
    user_id = sa.Column(
        sa.String(length=255), sa.ForeignKey("user.id"), primary_key=True
    )

    credit_group = relationship("CreditGroup", back_populates="users")
    user = relationship("User", back_populates="credit_groups")


class CreditGroup(Base):
    """SQLAlchemy model for the credit group table"""

    __tablename__ = "token_tracking_credit_group"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = sa.Column(sa.String(length=255))
    max_credit = sa.Column(sa.Integer())
    description = sa.Column(sa.String(length=255))

    users = relationship("CreditGroupUser", back_populates="credit_group")

    __table_args__ = (
        sa.Index(
            "idx_token_tracking_credit_group_name_lower",
            sa.func.lower(name),
            unique=True,
        ),
    )
