"""
Seeds the database with the same demo listings the original frontend-only
prototype had hardcoded, plus a demo user that owns them.

Run with:  python -m app.seed   (from the backend/ directory)
"""

from .database import SessionLocal, engine
from . import models
from .security import hash_password

models.Base.metadata.create_all(bind=engine)

DEMO_LISTINGS = [
    {"type": "Condo", "title": "Condo for Rent", "location": "Boeung Keng Kong", "floor": 12, "rent": 500, "tint": "#f4c95d", "owner_phone": "855 933456789"},
    {"type": "Condo", "title": "Condo for Rent", "location": "Toul Kork", "floor": 9, "rent": 650, "tint": "#5b6bd6", "owner_phone": "855 912345678"},
    {"type": "Apartment", "title": "Apartment for Rent", "location": "Toul Tom Pong", "floor": 5, "rent": 800, "tint": "#3fa7c9", "owner_phone": "855 933456789"},
    {"type": "Apartment", "title": "Apartment for Rent", "location": "Boeung Keng Kong", "floor": 3, "rent": 350, "tint": "#7d6fd1", "owner_phone": "855 977111222"},
    {"type": "Studio", "title": "Studio for Rent", "location": "Koh Pich", "floor": 2, "rent": 250, "tint": "#e08a9d", "owner_phone": "855 966333444"},
]


def run():
    db = SessionLocal()
    try:
        owner = db.query(models.User).filter(models.User.email == "demo@homerental.app").first()
        if not owner:
            owner = models.User(
                name="Demo Landlord",
                email="demo@homerental.app",
                hashed_password=hash_password("password123"),
                phone="855 933456789",
            )
            db.add(owner)
            db.commit()
            db.refresh(owner)
            print(f"Created demo user: {owner.email} / password123")

        if db.query(models.Listing).count() == 0:
            for item in DEMO_LISTINGS:
                db.add(models.Listing(owner_id=owner.id, **item))
            db.commit()
            print(f"Seeded {len(DEMO_LISTINGS)} demo listings.")
        else:
            print("Listings already exist, skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
