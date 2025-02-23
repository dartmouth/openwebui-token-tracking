import sqlalchemy as sa

from .base import Base


class BaseSetting(Base):
    """SQLAlchemy model for the baseline settings table"""

    __tablename__ = "token_tracking_base_settings"

    setting_key = sa.Column(sa.String(length=255), primary_key=True)
    setting_value = sa.Column(sa.String(length=255))
    description = sa.Column(sa.String(length=255))
