import uuid

from sqlmodel import Session, select

from db import engine
from models import Department


def create_department(name: str) -> Department:
    name = name.strip()

    if not name:
        raise ValueError("Название подразделения не может быть пустым")

    with Session(engine) as session:
        existing_department = session.exec(
            select(Department).where(Department.name == name)
        ).first()

        if existing_department is not None:
            raise ValueError(
                f"Подразделение '{name}' уже существует"
            )

        department = Department(name=name)

        session.add(department)
        session.commit()
        session.refresh(department)

        return department


def get_department(department_id: uuid.UUID) -> Department:
    with Session(engine) as session:
        department = session.get(Department, department_id)

        if department is None:
            raise ValueError("Подразделение не найдено")

        return department


def get_departments() -> list[Department]:
    with Session(engine) as session:
        statement = select(Department).order_by(Department.name)

        return list(session.exec(statement).all())