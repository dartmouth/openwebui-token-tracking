import sqlalchemy as sa

from .base import Base


class BaseSetting(Base):
    """SQLAlchemy model for the baseline settings table

    Stores global configuration settings for the token tracking system as key-value pairs.
    Used for system-wide settings like default credit allowances and rate limits.
    """

    __tablename__ = "token_tracking_base_settings"

    setting_key = sa.Column(sa.String(length=255), primary_key=True)
    """Primary key representing the unique setting identifier"""
    setting_value = sa.Column(sa.String(length=255))
    """Value of the setting stored as a string (may need conversion to appropriate type when used)"""
    description = sa.Column(sa.String(length=255))
    """Human-readable description of what the setting controls and its purpose"""
