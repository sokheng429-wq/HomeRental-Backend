from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[schemas.ListingOut])
def list_listings(
    search: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Listing)
    if type and type.lower() != "all":
        query = query.filter(models.Listing.type.ilike(type))
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Listing.location.ilike(like))
            | (models.Listing.title.ilike(like))
            | (models.Listing.type.ilike(like))
        )
    return query.order_by(models.Listing.created_at.desc()).all()


@router.get("/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("", response_model=schemas.ListingOut)
def create_listing(
    payload: schemas.ListingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    title = payload.title or f"{payload.type} for Rent"
    listing = models.Listing(
        owner_id=current_user.id,
        type=payload.type,
        title=title,
        location=payload.location,
        floor=payload.floor,
        rent=payload.rent,
        description=payload.description,
        owner_phone=payload.owner_phone or current_user.phone,
        tint=payload.tint or "#5b6bd6",
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this listing")
    db.delete(listing)
    db.commit()
    return {"ok": True}
