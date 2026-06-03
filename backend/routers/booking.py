from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import list_bookings, get_booking, update_booking_status

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


class StatusUpdate(BaseModel):
    status: str  # pending | confirmed | cancelled


@router.get("/")
def get_all_bookings():
    """List all bookings (newest first)."""
    return list_bookings()


@router.get("/{booking_id}")
def get_single_booking(booking_id: int):
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/status")
def patch_status(booking_id: int, body: StatusUpdate):
    """Update booking status: pending | confirmed | cancelled"""
    ok = update_booking_status(booking_id, body.status)
    if not ok:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"ok": True, "booking_id": booking_id, "status": body.status}
