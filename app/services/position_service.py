import uuid

from sqlmodel import Session, select

from db import engine
from models import Position


def create_position(name: str) -> Position:
    name = name.strip()

    if not name:
        raise ValueError("Название должности не может быть пустым")

    with Session(engine) as session:
        existing_position = session.exec(
            select(Position).where(Position.name == name)
        ).first()

        if existing_position is not None:
            raise ValueError(
                f"Должность '{name}' уже существует"
            )

        position = Position(name=name)

        session.add(position)
        session.commit()
        session.refresh(position)

        return position


def get_position(position_id: uuid.UUID) -> Position:
    with Session(engine) as session:
        position = session.get(Position, position_id)

        if position is None:
            raise ValueError("Должность не найдена")

        return position


def get_positions() -> list[Position]:
    with Session(engine) as session:
        statement = select(Position).order_by(Position.name)

        return list(session.exec(statement).all())