from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.types import JSON
from .database import DeclarativeBase

class EventModel(DeclarativeBase):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    organizer = Column(String, nullable=False)
    slots = Column(JSON, nullable=False, default=[])
    max_bookings = Column(Integer, nullable=False, default=1)

class BookingModel(DeclarativeBase):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    attendee_name = Column(String, nullable=False)
    attendee_email = Column(String, nullable=False)
    booked_at = Column(DateTime, nullable=False)
    slot = Column(String, nullable=False)