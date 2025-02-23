from sqlalchemy.orm import relationship
import sqlalchemy as sa

from .base import Base


class User(Base):
    """SQLAlchemy model for the user table.

    Mocks (parts of) the user table managed by Open WebUI
    and is only used for testing purposes.
    """

    __tablename__ = "user"
    id = sa.Column(sa.String(length=255), primary_key=True)
    name = sa.Column(sa.String(length=255))
    email = sa.Column(sa.String(length=255))

    credit_groups = relationship("CreditGroupUser", back_populates="user")
