from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB: fallback for creation
        server_onupdate=func.now(),  # DB: fallback for updates
        nullable=False,
    )
