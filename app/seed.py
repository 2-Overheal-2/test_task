from __future__ import annotations

import uuid
from datetime import UTC, timedelta

from faker import Faker
from sqlalchemy import insert, text
from sqlmodel import Session

from db import engine
from models import Department, Employee, Position, Request, RequestStatus


EMPLOYEE_COUNT = 1_000
REQUEST_COUNT = 1_000_000
REQUEST_BATCH_SIZE = 10_000

DEPARTMENT_COUNT = 20
POSITION_COUNT = 50
DESCRIPTION_POOL_SIZE = 1_000

SEED = 42


fake = Faker("ru_RU")
Faker.seed(SEED)

def clear_database() -> None:
    with Session(engine) as session:
        session.execute(
            text(
                """
                TRUNCATE TABLE
                    request,
                    employee,
                    position,
                    department
                CASCADE
                """
            )
        )
        session.commit()

    print("Таблицы очищены")


def seed_departments(count: int = DEPARTMENT_COUNT) -> list[uuid.UUID]:
    rows: list[dict] = []
    used_names: set[str] = set()

    while len(rows) < count:
        name = fake.company()

        if name in used_names:
            continue

        used_names.add(name)

        rows.append(
            {
                "id": uuid.uuid4(),
                "name": name,
            }
        )

    with Session(engine) as session:
        session.execute(
            insert(Department),
            rows,
        )
        session.commit()

    return [row["id"] for row in rows]


def seed_positions(count: int = POSITION_COUNT) -> list[uuid.UUID]:
    rows: list[dict] = []
    used_names: set[str] = set()

    while len(rows) < count:
        name = fake.job()

        if name in used_names:
            continue

        used_names.add(name)

        rows.append(
            {
                "id": uuid.uuid4(),
                "name": name,
            }
        )

    with Session(engine) as session:
        session.execute(
            insert(Position),
            rows,
        )
        session.commit()

    return [row["id"] for row in rows]


def seed_employees(department_ids: list[uuid.UUID], position_ids: list[uuid.UUID], count: int = EMPLOYEE_COUNT) -> list[uuid.UUID]:
    if not department_ids:
        raise ValueError("Список подразделений пуст")

    if not position_ids:
        raise ValueError("Список должностей пуст")

    rows: list[dict] = []

    for employee_number in range(1, count + 1):
        rows.append({
                "id": uuid.uuid4(),
                "full_name": (
                    f"{fake.name()}"
                ),
                "department_id": fake.random_element(
                    elements=department_ids
                ),
                "position_id": fake.random_element(
                    elements=position_ids
                ),
            })

    with Session(engine) as session:
        session.execute(insert(Employee),rows)
        session.commit()

    return [row["id"] for row in rows]


def generate_description_pool(
    count: int = DESCRIPTION_POOL_SIZE,
) -> list[str]:
    return [
        fake.text(max_nb_chars=200).replace(
            "\n",
            " ",
        )
        for _ in range(count)
    ]


def build_request_batch(*,start_number: int, batch_size: int, employee_ids: list[uuid.UUID], descriptions: list[str]) -> list[dict]:
    rows: list[dict] = []

    for offset in range(batch_size):
        request_number = start_number + offset

        created_at = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=UTC)

        due_date = (created_at.date() + timedelta(days=fake.random_int(min=-30, max=90)))

        rows.append(
            {
                "id": uuid.uuid4(),
                "number": request_number,
                "description": fake.random_element(
                    elements=descriptions
                ),
                "author_id": fake.random_element(
                    elements=employee_ids
                ),
                "assigned_to_id": fake.random_element(
                    elements=employee_ids
                ),
                "created_at": created_at,
                "due_date": due_date,
                "status": fake.random_element(
                    elements=list(RequestStatus)
                )}
        )

    return rows


def seed_requests(employee_ids: list[uuid.UUID], count: int = REQUEST_COUNT, batch_size: int = REQUEST_BATCH_SIZE) -> None:
    descriptions = generate_description_pool()
    inserted_count = 0

    with Session(engine) as session:
        while inserted_count < count:
            current_batch_size = min(batch_size, count - inserted_count)

            rows = build_request_batch(
                start_number=inserted_count + 1,
                batch_size=current_batch_size,
                employee_ids=employee_ids,
                descriptions=descriptions,
            )

            session.execute(insert(Request), rows)
            session.commit()

            inserted_count += current_batch_size


def update_database_statistics() -> None:
    with Session(engine) as session:
        session.execute(text("ANALYZE department"))
        session.execute(text("ANALYZE position"))
        session.execute(text("ANALYZE employee"))
        session.execute(text("ANALYZE request"))
        session.commit()

    print("Статистика PostgreSQL обновлена")


def seed_all() -> None:
    print("Генерации данных")

    clear_database()

    department_ids = seed_departments()
    position_ids = seed_positions()

    employee_ids = seed_employees(department_ids=department_ids, position_ids=position_ids)

    seed_requests(employee_ids=employee_ids)

    update_database_statistics()

    print("Генерация завершена")


if __name__ == "__main__":
    seed_all()