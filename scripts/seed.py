"""
Seed script — inserts 1000 books if the books table is empty.

Auto-run on startup via docker/entrypoint.sh.
Manual run:
    python scripts/seed.py        # inside container
    just seed                     # via justfile
"""
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta

from sqlalchemy import text

sys.path.insert(0, "/app")

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.book import Book  # noqa: E402

# ---------------------------------------------------------------------------
# Data pools
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
    "Joseph", "Karen", "Thomas", "Sarah", "Charles", "Lisa", "Haruki",
    "Chimamanda", "Gabriel", "Kazuo", "Toni", "Umberto", "Milan", "Jorge",
    "Fyodor", "Leo", "Virginia", "Sylvia", "Cormac", "Philip", "Ursula",
    "Octavia", "Isaac", "Arthur", "Agatha", "Raymond",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Wilson", "Anderson", "Murakami", "Adichie", "García Márquez",
    "Ishiguro", "Morrison", "Eco", "Kundera", "Borges", "Dostoevsky",
    "Tolstoy", "Woolf", "Plath", "McCarthy", "Dick", "Le Guin", "Butler",
    "Asimov", "Clarke", "Christie", "Carver",
]

TITLE_PREFIXES = [
    "The", "A", "Of", "In", "Beyond the", "Beneath the", "After the",
    "Before the", "Under the", "Above the", "Lost", "Hidden", "Dark",
    "Bright", "Last", "First", "Final", "Secret", "Ancient", "Silent",
]

TITLE_NOUNS = [
    "Shadow", "Light", "River", "Mountain", "City", "Garden", "Door",
    "Mirror", "Storm", "Wind", "Fire", "Ocean", "Forest", "Dream", "Night",
    "Morning", "Clock", "Letter", "Map", "Road", "Library", "Labyrinth",
    "House", "Tower", "Island", "Kingdom", "Empire", "Silence", "Voice",
    "Memory", "Echo", "Star", "Moon", "Sun", "Sky", "World", "Universe",
    "War", "Peace", "Love", "Time", "Truth", "Lie", "Fate", "Chance",
]

TITLE_SUFFIXES = [
    "", "", "", "",  # most titles have no suffix (weighted)
    "of Ruin", "of Hope", "of the Lost", "of Eternity", "Revisited",
    "Remembered", "Forgotten", "Reborn", "Rising", "Falling",
]


def random_author() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_title() -> str:
    prefix = random.choice(TITLE_PREFIXES)
    noun = random.choice(TITLE_NOUNS)
    suffix = random.choice(TITLE_SUFFIXES)
    title = f"{prefix} {noun}"
    if suffix:
        title += f" {suffix}"
    return title


def random_created_at() -> datetime:
    """Spread created_at over the last 3 years for realistic pagination data."""
    days_ago = random.randint(0, 3 * 365)
    return datetime.utcnow() - timedelta(days=days_ago, seconds=random.randint(0, 86400))


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

async def seed_books(count: int = 1000) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM books"))
        existing = result.scalar()

        if existing >= count:
            print(f"Books seed skipped — {existing} books already exist.")
            return

        to_insert = count - existing
        print(f"Seeding {to_insert} books (existing={existing})...")

        books = []
        for _ in range(to_insert):
            created_at = random_created_at()
            books.append(
                Book(
                    id=uuid.uuid4(),
                    title=random_title(),
                    author=random_author(),
                    published_year=random.randint(1900, 2025) if random.random() > 0.1 else None,
                    created_at=created_at,
                    updated_at=created_at,
                )
            )

        batch_size = 200
        for i in range(0, len(books), batch_size):
            session.add_all(books[i : i + batch_size])
            await session.commit()
            print(f"  {min(i + batch_size, len(books))}/{to_insert} inserted")

        print(f"Books seeded: {to_insert}")


if __name__ == "__main__":
    asyncio.run(seed_books())
