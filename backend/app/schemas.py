from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List

class EventBaseSchema(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    organizer: str
    slots: List[str] = []
    max_bookings: int

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @validator('start_time', 'end_time')
    def validate_times(cls, v, values, field):
        if field.name == 'end_time' and 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v

class EventCreateSchema(EventBaseSchema):
    pass

class EventSchema(EventBaseSchema):
    id: int

    class Config:
        from_attributes = True

class BookingBaseSchema(BaseModel):
    event_id: int
    attendee_name: str
    attendee_email: EmailStr
    booked_at: datetime
    slot: str

    @validator('attendee_name')
    def validate_attendee_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Attendee name cannot be empty")
        return v

class BookingCreateSchema(BookingBaseSchema):
    pass

class BookingSchema(BookingBaseSchema):
    id: int

    class Config:
        from_attributes = True