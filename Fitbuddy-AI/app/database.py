from datetime import datetime
from typing import Generator

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings


settings = get_settings()

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Database model for FitBuddy users and generated plans.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    goal: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    intensity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


def init_db() -> None:
    """
    Create database tables if they don't already exist.
    """

    Base.metadata.create_all(
        bind=engine
    )


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI database dependency.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def save_user(
    db: Session,
    *,
    user_id: str,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    original_plan: str,
    nutrition_tip: str,
) -> User:

    existing_user = db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )

    if existing_user is None:

        user = User(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(user)

    else:

        existing_user.username = username
        existing_user.age = age
        existing_user.weight = weight
        existing_user.goal = goal
        existing_user.intensity = intensity

        existing_user.original_plan = original_plan
        existing_user.updated_plan = None
        existing_user.nutrition_tip = nutrition_tip
        existing_user.updated_at = None

        user = existing_user

    db.commit()

    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )


def update_plan(
    db: Session,
    user: User,
    updated_plan: str,
    nutrition_tip: str,
) -> User:

    user.updated_plan = updated_plan

    user.nutrition_tip = nutrition_tip

    user.updated_at = datetime.utcnow()

    db.commit()

    db.refresh(user)

    return user


def get_all_users(
    db: Session,
) -> list[User]:

    return list(
        db.scalars(
            select(User).order_by(
                User.created_at.desc()
            )
        ).all()
    )