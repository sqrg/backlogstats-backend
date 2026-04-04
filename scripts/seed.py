"""Idempotent seed script.

Run via:
    seed                  (after pip install -e .)
    python -m scripts.seed
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

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


def _get_or_create_user(db: Session, email: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        user = User(email=email)
        db.add(user)
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
    alice = _get_or_create_user(db, "alice@example.com")
    bob = _get_or_create_user(db, "bob@example.com")
    charlie = _get_or_create_user(db, "charlie@example.com")

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


if __name__ == "__main__":
    main()
