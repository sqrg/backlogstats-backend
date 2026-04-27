"""Idempotent seed script.

Run via:
    seed                  (after pip install -e .)
    python -m scripts.seed
"""

import random
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.company import Company
from app.models.game import Game
from app.models.game_genre import GameGenre
from app.models.game_in_collection import GameInCollection
from app.models.genre import Genre
from app.models.platform import Platform
from app.models.playthrough import Playthrough, PlaythroughStatus
from app.models.user import User
from app.models.user_list import UserList
from app.models.user_list_entry import UserListEntry


def _get_or_create_user(
    db: Session, email: str, password: str | None = None
) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        user = User(
            email=email,
            hashed_password=hash_password(password) if password else None,
        )
        db.add(user)
        db.flush()
    elif password and not user.hashed_password:
        user.hashed_password = hash_password(password)
        db.flush()
    return user


def _get_or_create_company(db: Session, name: str) -> Company:
    company = db.execute(
        select(Company).where(Company.name == name)
    ).scalar_one_or_none()
    if not company:
        company = Company(name=name)
        db.add(company)
        db.flush()
    return company


def _get_or_create_platform(db: Session, name: str, company_id: int | None) -> Platform:
    platform = db.execute(
        select(Platform).where(Platform.name == name)
    ).scalar_one_or_none()
    if not platform:
        platform = Platform(name=name, company_id=company_id)
        db.add(platform)
        db.flush()
    return platform


def _get_or_create_genre(db: Session, name: str) -> Genre:
    genre = db.execute(select(Genre).where(Genre.name == name)).scalar_one_or_none()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre


def _get_or_create_game(db: Session, name: str, igdb_id: int | None = None) -> Game:
    if igdb_id is not None:
        game = db.execute(
            select(Game).where(Game.igdb_id == igdb_id)
        ).scalar_one_or_none()
    else:
        game = db.execute(
            select(Game).where(Game.name == name, Game.igdb_id.is_(None))
        ).scalar_one_or_none()
    if not game:
        game = Game(name=name, igdb_id=igdb_id)
        db.add(game)
        db.flush()
    return game


def _get_or_create_game_genre(db: Session, game_id: int, genre_id: int) -> GameGenre:
    gg = db.execute(
        select(GameGenre).where(
            GameGenre.game_id == game_id, GameGenre.genre_id == genre_id
        )
    ).scalar_one_or_none()
    if not gg:
        gg = GameGenre(game_id=game_id, genre_id=genre_id)
        db.add(gg)
        db.flush()
    return gg


def _get_or_create_collection_entry(
    db: Session, user_id: int, game_id: int, platform_id: int
) -> GameInCollection:
    entry = db.execute(
        select(GameInCollection).where(
            GameInCollection.user_id == user_id,
            GameInCollection.game_id == game_id,
            GameInCollection.platform_id == platform_id,
        )
    ).scalar_one_or_none()
    if not entry:
        entry = GameInCollection(
            user_id=user_id, game_id=game_id, platform_id=platform_id
        )
        db.add(entry)
        db.flush()
    return entry


def _get_or_create_playthrough(
    db: Session,
    game_in_collection_id: int,
    status: PlaythroughStatus,
    started_at: date | None = None,
    completed_at: date | None = None,
    completion_time: int | None = None,
    notes: str | None = None,
) -> Playthrough:
    # Keyed on collection entry + status; one playthrough per status per entry.
    pt = db.execute(
        select(Playthrough).where(
            Playthrough.game_in_collection_id == game_in_collection_id,
            Playthrough.status == status,
        )
    ).scalar_one_or_none()
    if not pt:
        pt = Playthrough(
            game_in_collection_id=game_in_collection_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            completion_time=completion_time,
            notes=notes,
        )
        db.add(pt)
        db.flush()
    return pt


def _get_or_create_user_list(
    db: Session, user_id: int, name: str, is_public: bool
) -> UserList:
    ul = db.execute(
        select(UserList).where(UserList.user_id == user_id, UserList.name == name)
    ).scalar_one_or_none()
    if not ul:
        ul = UserList(user_id=user_id, name=name, is_public=is_public)
        db.add(ul)
        db.flush()
    return ul


def _get_or_create_list_entry(
    db: Session, list_id: int, game_id: int, position: int | None = None
) -> UserListEntry:
    le = db.execute(
        select(UserListEntry).where(
            UserListEntry.list_id == list_id, UserListEntry.game_id == game_id
        )
    ).scalar_one_or_none()
    if not le:
        le = UserListEntry(list_id=list_id, game_id=game_id, position=position)
        db.add(le)
        db.flush()
    return le


def main() -> None:
    db = SessionLocal()
    try:
        _seed(db)
        db.commit()
        print("Seed complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _seed(db: Session) -> None:
    # ── Users ────────────────────────────────────────────────────────────────
    alice = _get_or_create_user(db, "alice@example.com", password="password123")
    bob = _get_or_create_user(db, "bob@example.com", password="password123")
    charlie = _get_or_create_user(db, "charlie@example.com", password="password123")

    # ── Companies ────────────────────────────────────────────────────────────
    sony = _get_or_create_company(db, "Sony")
    nintendo = _get_or_create_company(db, "Nintendo")
    microsoft = _get_or_create_company(db, "Microsoft")

    # ── Platforms ────────────────────────────────────────────────────────────
    ps5 = _get_or_create_platform(db, "PS5", sony.id)
    switch = _get_or_create_platform(db, "Nintendo Switch", nintendo.id)
    xbox = _get_or_create_platform(db, "Xbox Series X", microsoft.id)
    pc = _get_or_create_platform(db, "PC", None)

    # ── Genres ───────────────────────────────────────────────────────────────
    rpg = _get_or_create_genre(db, "RPG")
    action = _get_or_create_genre(db, "Action")
    strategy = _get_or_create_genre(db, "Strategy")

    # ── Games ─────────────────────────────────────────────────────────────────
    # IGDB-sourced (igdb_id set)
    witcher3 = _get_or_create_game(db, "The Witcher 3: Wild Hunt", igdb_id=1942)
    elden_ring = _get_or_create_game(db, "Elden Ring", igdb_id=119133)
    # Manually created (igdb_id is None)
    backlog_quest = _get_or_create_game(db, "Backlog Quest")
    chronicles = _get_or_create_game(db, "Chronicles of Strategy")
    dragons_keep = _get_or_create_game(db, "Dragon's Keep")

    # ── GameGenre associations ────────────────────────────────────────────────
    _get_or_create_game_genre(db, witcher3.id, rpg.id)
    _get_or_create_game_genre(db, witcher3.id, action.id)
    _get_or_create_game_genre(db, elden_ring.id, rpg.id)
    _get_or_create_game_genre(db, elden_ring.id, action.id)
    _get_or_create_game_genre(db, backlog_quest.id, rpg.id)
    _get_or_create_game_genre(db, chronicles.id, strategy.id)
    _get_or_create_game_genre(db, dragons_keep.id, rpg.id)
    _get_or_create_game_genre(db, dragons_keep.id, strategy.id)

    # ── GameInCollection ─────────────────────────────────────────────────────
    alice_witcher = _get_or_create_collection_entry(db, alice.id, witcher3.id, ps5.id)
    alice_elden = _get_or_create_collection_entry(db, alice.id, elden_ring.id, ps5.id)
    bob_elden = _get_or_create_collection_entry(db, bob.id, elden_ring.id, xbox.id)
    bob_chronicles = _get_or_create_collection_entry(db, bob.id, chronicles.id, pc.id)
    charlie_dragons = _get_or_create_collection_entry(
        db, charlie.id, dragons_keep.id, switch.id
    )
    charlie_backlog = _get_or_create_collection_entry(
        db, charlie.id, backlog_quest.id, pc.id
    )

    # ── Playthroughs ─────────────────────────────────────────────────────────
    _get_or_create_playthrough(
        db,
        alice_witcher.id,
        PlaythroughStatus.COMPLETED,
        started_at=date(2024, 1, 1),
        completed_at=date(2024, 3, 15),
        completion_time=80,
        notes="Amazing game, loved every moment.",
    )
    _get_or_create_playthrough(
        db,
        alice_elden.id,
        PlaythroughStatus.PLAYING,
        started_at=date(2024, 4, 1),
    )
    _get_or_create_playthrough(
        db,
        bob_elden.id,
        PlaythroughStatus.ON_HOLD,
        started_at=date(2024, 2, 10),
        notes="Taking a break, will return.",
    )
    _get_or_create_playthrough(
        db,
        bob_chronicles.id,
        PlaythroughStatus.NOT_STARTED,
    )
    _get_or_create_playthrough(
        db,
        charlie_dragons.id,
        PlaythroughStatus.ABANDONED,
        started_at=date(2024, 2, 1),
        notes="Not for me.",
    )
    _get_or_create_playthrough(
        db,
        charlie_backlog.id,
        PlaythroughStatus.NOT_STARTED,
    )

    # ── UserLists ─────────────────────────────────────────────────────────────
    alice_list = _get_or_create_user_list(
        db, alice.id, "2024 Completions", is_public=True
    )
    bob_list = _get_or_create_user_list(db, bob.id, "Wishlist", is_public=False)

    # ── UserListEntries ───────────────────────────────────────────────────────
    _get_or_create_list_entry(db, alice_list.id, witcher3.id, position=1)
    _get_or_create_list_entry(db, alice_list.id, elden_ring.id, position=2)
    _get_or_create_list_entry(db, bob_list.id, dragons_keep.id, position=1)

    # ── Bulk dummy data for stats page ───────────────────────────────────────
    _seed_bulk_for_stats(db, alice.id)


_BULK_GENRE_NAMES = [
    "Adventure",
    "Shooter",
    "Puzzle",
    "Platformer",
    "Indie",
    "Simulation",
    "Sports",
    "Racing",
    "Fighting",
    "Horror",
    "Roguelike",
    "Survival",
]

_BULK_GAME_TITLES = [
    # Synthetic, evocative titles — 120 unique entries.
    "Echoes of the Hollow", "Skyborne Saga", "Crimson Tides", "Neon Drift",
    "Whispers Below", "Ironclad Dawn", "Lunar Vagabond", "Pixel Reverie",
    "Forsaken Atlas", "Silent Cartographer", "The Last Embers", "Veiled Horizons",
    "Ashen Reverence", "Cobalt Pact", "Driftwood Hollow", "Embered Skies",
    "Frostbound Legacy", "Glimmer Protocol", "Hollow Compass", "Inkwell Knights",
    "Jagged Spires", "Karma Engine", "Lantern Run", "Midnight Bazaar",
    "Nimbus Architect", "Oaken Reverie", "Phantom Causeway", "Quartz Dominion",
    "Ravens of Ardor", "Solace Drift", "Tessellate", "Umbra Trial",
    "Verdant Hollow", "Whisperwind Heir", "Xenith Cycle", "Yarrow Knight",
    "Zephyr Logic", "Asteroid Garden", "Brimstone Crown", "Cinder Glade",
    "Dauntless Few", "Ember Tide", "Falconer's Errand", "Glasswing",
    "Hearthlight", "Iron Lullaby", "Jubilee Run", "Kelpwood",
    "Lichgate", "Mossy Vault", "Nightingale Pact", "Obsidian Tea",
    "Pollen Wars", "Quill of Ardor", "Rustfall", "Sablefen",
    "Tideforger", "Underglow", "Vellichor", "Wickerline",
    "Xolotl's Run", "Yonderlight", "Zenithfall", "Auric Lighthouse",
    "Beast of Belham", "Charcoal Sky", "Dovetail Heist", "Embershade",
    "Fjord and Fang", "Glassroot", "Halcyon Drive", "Inertia Garden",
    "Junebug Coda", "Kindling Wars", "Loomwarden", "Mirthbound",
    "Nullspace Tango", "Opalpath", "Petrichor Trial", "Quillvale",
    "Reedrunner", "Sallowshire", "Talespine", "Underloom",
    "Veridian Cipher", "Whisper Tactics", "Xenotype", "Yoke of Stars",
    "Zoetrope Run", "Antlerwood", "Brimstone Carnival", "Cardinal Drift",
    "Duskling", "Ember Atlas", "Forgewright", "Gravelight",
    "Hushrook", "Inkbound Tale", "Jasper's Gambit", "Kithforge",
    "Lacuna Heir", "Marrowbond", "Nettlewise", "Otherbloom",
    "Pyrelock", "Quietnaut", "Riverling", "Stagcoat",
    "Thornglass", "Umbral Roost", "Voivode's End", "Wanderwell",
    "Xanadu Spiral", "Yarrowkeep", "Zealot's Carriage", "Amberhowl",
    "Boneharrow", "Coldhearth", "Dustwoven", "Embergale",
    "Faewright", "Gildmark", "Husk and Halo", "Ironseam",
]


def _seed_bulk_for_stats(db: Session, user_id: int) -> None:
    """Generate ~120 games + collection entries + playthroughs for one user.

    Idempotent: skips if the first generated game already exists.
    Uses a fixed random seed so re-runs produce a stable dataset.
    """
    if not _BULK_GAME_TITLES:
        return
    sentinel_name = _BULK_GAME_TITLES[0]
    existing = db.execute(
        select(Game).where(Game.name == sentinel_name, Game.igdb_id.is_(None))
    ).scalar_one_or_none()
    if existing is not None:
        return

    rng = random.Random(42)

    platforms = db.execute(select(Platform)).scalars().all()
    if not platforms:
        return

    genres = [_get_or_create_genre(db, name) for name in _BULK_GENRE_NAMES]
    # Pull in any pre-existing genres too (RPG, Action, Strategy).
    all_genres = db.execute(select(Genre)).scalars().all()
    if all_genres:
        genres = all_genres

    today = date.today()
    earliest = today - timedelta(days=365)

    # Status mix: weight COMPLETED heavily so completion charts are populated,
    # but include the full status palette so breakdowns/cards have variety.
    primary_statuses = (
        [PlaythroughStatus.COMPLETED] * 70
        + [PlaythroughStatus.PLAYING] * 10
        + [PlaythroughStatus.ON_HOLD] * 7
        + [PlaythroughStatus.ABANDONED] * 8
        + [PlaythroughStatus.NOT_STARTED] * 5
    )

    for title in _BULK_GAME_TITLES:
        game = _get_or_create_game(db, title)

        chosen_genres = rng.sample(genres, k=rng.randint(1, 2))
        for g in chosen_genres:
            _get_or_create_game_genre(db, game.id, g.id)

        platform = rng.choice(platforms)
        entry = _get_or_create_collection_entry(db, user_id, game.id, platform.id)

        primary = rng.choice(primary_statuses)
        _make_bulk_playthrough(db, entry.id, primary, today, earliest, rng)

        # ~15% of games get a second playthrough to mimic replays / abandons.
        if rng.random() < 0.15 and primary != PlaythroughStatus.NOT_STARTED:
            second_choices = [
                s
                for s in PlaythroughStatus
                if s != primary and s != PlaythroughStatus.NOT_STARTED
            ]
            second = rng.choice(second_choices)
            _make_bulk_playthrough(db, entry.id, second, today, earliest, rng)


def _make_bulk_playthrough(
    db: Session,
    entry_id: int,
    status: PlaythroughStatus,
    today: date,
    earliest: date,
    rng: random.Random,
) -> None:
    """Insert a playthrough with status-appropriate dates and times.

    Uses _get_or_create_playthrough's (entry, status) idempotency key, so
    re-running won't duplicate.
    """
    span_days = (today - earliest).days

    if status == PlaythroughStatus.COMPLETED:
        completed_at = earliest + timedelta(days=rng.randint(0, span_days))
        play_window = rng.randint(7, 180)
        started_at = completed_at - timedelta(days=play_window)
        completion_time = rng.randint(8, 120)
        _get_or_create_playthrough(
            db,
            entry_id,
            status,
            started_at=started_at,
            completed_at=completed_at,
            completion_time=completion_time,
        )
    elif status == PlaythroughStatus.PLAYING:
        started_at = today - timedelta(days=rng.randint(1, 90))
        _get_or_create_playthrough(db, entry_id, status, started_at=started_at)
    elif status == PlaythroughStatus.ON_HOLD:
        started_at = earliest + timedelta(days=rng.randint(0, span_days))
        _get_or_create_playthrough(db, entry_id, status, started_at=started_at)
    elif status == PlaythroughStatus.ABANDONED:
        started_at = earliest + timedelta(days=rng.randint(0, span_days))
        _get_or_create_playthrough(db, entry_id, status, started_at=started_at)
    else:  # NOT_STARTED
        _get_or_create_playthrough(db, entry_id, status)


if __name__ == "__main__":
    main()
