"""
Rule-based rental assistant.

It is intentionally not an LLM call (no external API key required so the
whole thing runs fully locally), but unlike the original frontend-only demo
it now:
  - understands budgets written as "$500", "500 usd", "500/month", etc.
  - matches against real neighborhoods (from CAMBODIA_LOCATIONS style list)
  - actually queries the Listings table in Postgres for matches
  - remembers the last listing it suggested (per user) so "give me the
    owner's number" resolves to the right property
  - falls back to a helpful clarifying question when it doesn't have enough
    information yet

Swap `generate_reply` for a call to a real LLM (e.g. the Anthropic API)
later if you want free-form conversation - the DB lookup helpers below
(`find_matching_listings`, `get_last_suggested_listing`) are reusable either
way.
"""

import re
from typing import Optional

from sqlalchemy.orm import Session

from . import models

GREETING_RE = re.compile(r"\b(hi|hello|hey|sup|good (morning|afternoon|evening))\b", re.I)
CONTACT_RE = re.compile(r"\b(number|contact|owner|call|phone|whatsapp|telegram)\b", re.I)
THANKS_RE = re.compile(r"\b(thanks|thank you|thx|ty)\b", re.I)

BUDGET_RE = re.compile(r"\$?\s?(\d{2,5})\s?(usd|dollars?|per month|/month|a month)?", re.I)

LOCATION_KEYWORDS = [
    "toul tom pong", "boeung keng kong", "bkk1", "bkk", "toul kork",
    "koh pich", "chroy changvar", "chamkarmon", "daun penh", "sen sok",
    "russian market", "phnom penh", "siem reap", "battambang", "kampot",
    "sihanouk", "sihanoukville",
]


def _extract_budget(text: str) -> Optional[int]:
    match = BUDGET_RE.search(text)
    if match:
        try:
            return int(match.group(1))
        except (TypeError, ValueError):
            return None
    return None


def _extract_location(text: str) -> Optional[str]:
    lowered = text.lower()
    for loc in LOCATION_KEYWORDS:
        if loc in lowered:
            return loc
    return None


def find_matching_listings(
    db: Session, location: Optional[str], budget: Optional[int], limit: int = 1
):
    query = db.query(models.Listing)
    if location:
        query = query.filter(models.Listing.location.ilike(f"%{location}%"))

    listings = query.all()

    if budget:
        # sort by how close the rent is to the requested budget
        listings.sort(key=lambda l: abs(l.rent - budget))
    else:
        listings.sort(key=lambda l: l.created_at, reverse=True)

    return listings[:limit]


def get_last_suggested_listing(db: Session, user_id: int) -> Optional[models.Listing]:
    last = (
        db.query(models.ChatMessage)
        .filter(
            models.ChatMessage.user_id == user_id,
            models.ChatMessage.role == "bot",
            models.ChatMessage.listing_id.isnot(None),
        )
        .order_by(models.ChatMessage.created_at.desc())
        .first()
    )
    if last:
        return db.query(models.Listing).filter(models.Listing.id == last.listing_id).first()
    return None


def _describe(listing: models.Listing) -> str:
    floor_txt = f", floor {listing.floor}" if listing.floor else ""
    return f"{listing.type} for Rent · ${listing.rent:.0f}/MONTH · {listing.location}{floor_txt}"


def generate_reply(db: Session, user_id: int, text: str) -> tuple[str, Optional[int]]:
    """Returns (reply_text, listing_id_or_None)."""

    if THANKS_RE.search(text):
        return "You're welcome! Let me know if you want to see more places.", None

    if GREETING_RE.search(text) and len(text.split()) <= 4:
        return (
            "Hi! I'm here to help you find a room, apartment, or condo in Phnom Penh. "
            "Tell me a neighborhood and your monthly budget to get started.",
            None,
        )

    if CONTACT_RE.search(text):
        listing = get_last_suggested_listing(db, user_id)
        if listing and listing.owner_phone:
            return (
                f"Here you go: {listing.owner_phone}. Let me know if you'd like help lining up a viewing.",
                listing.id,
            )
        if listing:
            return (
                "That owner hasn't listed a phone number yet — try asking about another listing.",
                listing.id,
            )
        return (
            "Sure — which listing? Tell me a neighborhood and budget first and I'll pull one up.",
            None,
        )

    location = _extract_location(text)
    budget = _extract_budget(text)

    if location or budget:
        matches = find_matching_listings(db, location, budget, limit=1)
        if matches:
            listing = matches[0]
            extra = ""
            if budget and abs(listing.rent - budget) > 50:
                extra = " It's a bit outside your exact budget, but closest match I have."
            return (
                f"Got it. I found a {_describe(listing)}.{extra} Want the owner's number?",
                listing.id,
            )
        else:
            where = f" in {location.title()}" if location else ""
            budget_txt = f" around ${budget}/month" if budget else ""
            return (
                f"I don't have any listings{where}{budget_txt} right now. "
                "Try a nearby area, or check back after new posts come in.",
                None,
            )

    return (
        "Tell me a neighborhood (e.g. BKK1, Toul Tom Pong, Toul Kork) and your monthly "
        "budget and I'll pull up matching listings.",
        None,
    )
