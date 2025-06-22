from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from . import models, schemas

# --------------------- Event CRUD Operations ---------------------

async def add_event(session: AsyncSession, new_event: schemas.EventCreateSchema):
    event_obj = models.EventModel(**new_event.dict())
    session.add(event_obj)
    await session.commit()
    await session.refresh(event_obj)
    return event_obj

async def fetch_events(session: AsyncSession, offset: int = 0, limit: int = 10):
    query_result = await session.execute(select(models.EventModel).offset(offset).limit(limit))
    return query_result.scalars().all()

async def fetch_event_by_id(session: AsyncSession, event_id: int):
    query_result = await session.execute(select(models.EventModel).where(models.EventModel.id == event_id))
    return query_result.scalar_one_or_none()

async def modify_event(session: AsyncSession, event_id: int, update_data: schemas.EventCreateSchema):
    query_result = await session.execute(select(models.EventModel).where(models.EventModel.id == event_id))
    event_obj = query_result.scalar_one_or_none()
    if not event_obj:
        return None
    for key, value in update_data.dict().items():
        setattr(event_obj, key, value)
    await session.commit()
    await session.refresh(event_obj)
    return event_obj

async def remove_event(session: AsyncSession, event_id: int):
    query_result = await session.execute(select(models.EventModel).where(models.EventModel.id == event_id))
    event_obj = query_result.scalar_one_or_none()
    if not event_obj:
        return None
    await session.delete(event_obj)
    await session.commit()
    return event_obj

# --------------------- Booking CRUD Operations ---------------------

async def add_booking(session: AsyncSession, booking_data: schemas.BookingCreateSchema):
    booking_obj = models.BookingModel(**booking_data.dict())
    session.add(booking_obj)
    await session.commit()
    await session.refresh(booking_obj)
    return booking_obj

async def fetch_bookings(session: AsyncSession, offset: int = 0, limit: int = 10):
    query_result = await session.execute(select(models.BookingModel).offset(offset).limit(limit))
    return query_result.scalars().all()

async def fetch_bookings_for_event(session: AsyncSession, event_id: int, offset: int = 0, limit: int = 10):
    query_result = await session.execute(
        select(models.BookingModel).where(models.BookingModel.event_id == event_id).offset(offset).limit(limit)
    )
    return query_result.scalars().all()

async def fetch_booking_by_email_and_slot(session: AsyncSession, event_id: int, slot: str, attendee_email: str):
    query_result = await session.execute(
        select(models.BookingModel)
        .where(
            models.BookingModel.event_id == event_id,
            models.BookingModel.slot == slot,
            models.BookingModel.attendee_email == attendee_email,
        )
    )
    return query_result.scalar_one_or_none()

async def fetch_bookings_by_email(session: AsyncSession, email: str, offset: int = 0, limit: int = 20):
    query_result = await session.execute(
        select(models.BookingModel).where(models.BookingModel.attendee_email == email).offset(offset).limit(limit)
    )
    return query_result.scalars().all()

async def count_bookings_for_slot(session: AsyncSession, event_id: int, slot: str):
    query_result = await session.execute(
        select(func.count(models.BookingModel.id))
        .where(models.BookingModel.event_id == event_id, models.BookingModel.slot == slot)
    )
    return query_result.scalar()

async def modify_booking(session: AsyncSession, booking_id: int, update_data: schemas.BookingCreateSchema):
    query_result = await session.execute(select(models.BookingModel).where(models.BookingModel.id == booking_id))
    booking_obj = query_result.scalar_one_or_none()
    if not booking_obj:
        return None
    for key, value in update_data.dict().items():
        setattr(booking_obj, key, value)
    await session.commit()
    await session.refresh(booking_obj)
    return booking_obj

async def remove_booking(session: AsyncSession, booking_id: int):
    query_result = await session.execute(select(models.BookingModel).where(models.BookingModel.id == booking_id))
    booking_obj = query_result.scalar_one_or_none()
    if not booking_obj:
        return None
    await session.delete(booking_obj)
    await session.commit()
    return booking_obj

# --------------------- Validation Helpers ---------------------

async def is_valid_slot(event_obj, slot: str) -> bool:
    return slot in event_obj.slots

async def is_slot_open(session: AsyncSession, event_obj, slot: str) -> bool:
    current_count = await count_bookings_for_slot(session, event_obj.id, slot)
    return current_count < event_obj.max_bookings

async def add_booking_with_checks(session: AsyncSession, booking_data: schemas.BookingCreateSchema):
    event_obj = await fetch_event_by_id(session, booking_data.event_id)
    if not event_obj:
        raise ValueError("Event not found.")

    if not await is_valid_slot(event_obj, booking_data.slot):
        raise ValueError("Slot not valid for this event.")

    existing = await fetch_booking_by_email_and_slot(session, event_obj.id, booking_data.slot, booking_data.attendee_email)
    if existing:
        raise ValueError("You have already booked this slot.")

    if not await is_slot_open(session, event_obj, booking_data.slot):
        raise ValueError("Slot already fully booked.")

    booking_obj = models.BookingModel(**booking_data.dict())
    session.add(booking_obj)
    await session.commit()
    await session.refresh(booking_obj)
    return booking_obj