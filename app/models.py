"""Database models. A single `tickets` table holds every prediction and any
admin correction supplied later via /feedback."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_text = Column(Text, nullable=False)
    predicted_department = Column(String(64), nullable=False)
    # Filled in only when an admin corrects the prediction via /feedback.
    correct_department = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
