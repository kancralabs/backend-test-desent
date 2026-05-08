"""
Seed script — inserts 1000 books and 5 users into the database.

Usage (inside container):
    python scripts/seed.py

Usage (via justfile):
    just seed
"""
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, text

sys.path.insert(0, "/app")

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.book import Book  # noqa: E402
from app.models.user import User  # noqa: E402

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


def random_year() -> int:
    return random.randint(1900, 2025)


def random_created_at() -> datetime:
    """Spread created_at over the last 3 years for realistic pagination data."""
    days_ago = random.randint(0, 3 * 365)
    return datetime.utcnow() - timedelta(days=days_ago, seconds=random.randint(0, 86400))


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

SEED_USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123"},
    {"username": "alice", "email": "alice@example.com", "password": "alice123"},
    {"username": "bob", "email": "bob@example.com", "password": "bob12345"},
    {"username": "charlie", "email": "charlie@example.com", "password": "charlie1"},
    {"username": "diana", "email": "diana@example.com", "password": "diana123"},
]


async def seed_users(session) -> int:
    inserted = 0
    for data in SEED_USERS:
        existing = await session.execute(
            select(User).where(User.username == data["username"])
        )
        if existing.scalar_one_or_none():
            print(f"  [skip] user '{data['username']}' already exists")
            continue

        user = User(
            username=data["username"],
            email=data["email"],
            hashed_password=hash_password(data["password"]),
        )
        session.add(user)
        inserted += 1
        print(f"  [+] user '{data['username']}'")

    await session.commit()
    return inserted


async def seed_books(session, count: int = 1000) -> int:
    # Check existing count
    result = await session.execute(text("SELECT COUNT(*) FROM books"))
    existing_count = result.scalar()

    if existing_count >= count:
        print(f"  [skip] {existing_count} books already exist (target={count})")
        return 0

    to_insert = count - existing_count
    print(f"  Inserting {to_insert} books (existing={existing_count})...")

    books = []
    for _ in range(to_insert):
        created_at = random_created_at()
        books.append(
            Book(
                id=uuid.uuid4(),
                title=random_title(),
                author=random_author(),
                published_year=random_year() if random.random() > 0.1 else None,
                created_at=created_at,
                updated_at=created_at,
            )
        )

    # Bulk insert in batches of 200
    batch_size = 200
    for i in range(0, len(books), batch_size):
        batch = books[i : i + batch_size]
        session.add_all(batch)
        await session.commit()
        print(f"  [+] {min(i + batch_size, len(books))}/{to_insert} books inserted")

    return to_insert


async def main() -> None:
    print("=" * 50)
    print("  Seeding database")
    print("=" * 50)

    async with AsyncSessionLocal() as session:
        print("\n[Users]")
        users_inserted = await seed_users(session)

        print(f"\n[Books] (target: 1000)")
        books_inserted = await seed_books(session, count=1000)

    print("\n" + "=" * 50)
    print(f"  Done! users={users_inserted}  books={books_inserted}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
