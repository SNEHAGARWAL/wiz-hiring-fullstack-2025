from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from . import models, schemas, crud
from .database import acquire_session

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root_message():
    return {"message": "Hello, Mini-Calendly backend is working!"}

# Event endpoints
@app.post("/events/", response_model=schemas.EventSchema)
async def create_event(event_data: schemas.EventCreateSchema, session: AsyncSession = Depends(acquire_session)):
    return await crud.add_event(session, event_data)

@app.get("/events/", response_model=List[schemas.EventSchema])
async def get_events(offset: int = 0, limit: int = 10, session: AsyncSession = Depends(acquire_session)):
    return await crud.fetch_events(session, offset=offset, limit=limit)

@app.get("/events/{event_id}", response_model=schemas.EventSchema)
async def get_event(event_id: int, session: AsyncSession = Depends(acquire_session)):
    event_obj = await crud.fetch_event_by_id(session, event_id)
    if event_obj is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_obj

@app.put("/events/{event_id}/", response_model=schemas.EventSchema)
async def update_event(event_id: int, update_data: schemas.EventCreateSchema, session: AsyncSession = Depends(acquire_session)):
    updated_event = await crud.modify_event(session, event_id, update_data)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@app.delete("/events/{event_id}/", response_model=schemas.EventSchema)
async def delete_event(event_id: int, session: AsyncSession = Depends(acquire_session)):
    deleted_event = await crud.remove_event(session, event_id)
    if deleted_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return deleted_event

# Booking endpoints
@app.post("/bookings/", response_model=schemas.BookingSchema)
async def create_booking(booking_data: schemas.BookingCreateSchema, session: AsyncSession = Depends(acquire_session)):
    return await crud.add_booking(session, booking_data)

@app.get("/bookings/", response_model=List[schemas.BookingSchema])
async def get_bookings(offset: int = 0, limit: int = 10, session: AsyncSession = Depends(acquire_session)):
    return await crud.fetch_bookings(session, offset=offset, limit=limit)

@app.get("/events/{event_id}/bookings/", response_model=List[schemas.BookingSchema])
async def get_bookings_for_event(
    event_id: int, offset: int = 0, limit: int = 10, session: AsyncSession = Depends(acquire_session)
):
    return await crud.fetch_bookings_for_event(session, event_id=event_id, offset=offset, limit=limit)

@app.put("/bookings/{booking_id}/", response_model=schemas.BookingSchema)
async def update_booking(booking_id: int, update_data: schemas.BookingCreateSchema, session: AsyncSession = Depends(acquire_session)):
    updated_booking = await crud.modify_booking(session, booking_id, update_data)
    if updated_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return updated_booking

@app.delete("/bookings/{booking_id}/", response_model=schemas.BookingSchema)
async def delete_booking(booking_id: int, session: AsyncSession = Depends(acquire_session)):
    deleted_booking = await crud.remove_booking(session, booking_id)
    if deleted_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return deleted_booking

@app.post("/events/{event_id}/bookings", response_model=schemas.BookingSchema)
async def book_slot_for_event(
    event_id: int,
    booking_data: schemas.BookingCreateSchema,
    session: AsyncSession = Depends(acquire_session)
):
    try:
        booking = await crud.add_booking_with_checks(session, booking_data)
        return booking
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/users/{email}/bookings", response_model=List[schemas.BookingSchema])
async def get_bookings_by_email(
    email: str,
    session: AsyncSession = Depends(acquire_session),
    offset: int = 0,
    limit: int = 20
):
    return await crud.fetch_bookings_by_email(session, email=email, offset=offset, limit=limit)