from uuid import UUID

from sqlmodel import Session, select

from db import engine
from models import Department, Employee, Position


def create_employee(full_name: str, department_id: UUID, position_id: UUID):
    full_name = full_name.strip()

    if not full_name:
        raise ValueError("ФИО сотрудника не может быть пустым")

    with Session(engine) as session:
        department = session.get(Department, department_id)

        if department is None:
            raise ValueError("Подразделение не найдено")

        position = session.get(Position, position_id)

        if position is None:
            raise ValueError("Должность не найдена")

        employee = Employee(
            full_name=full_name,
            department_id=department_id,
            position_id=position_id,
        )

        session.add(employee)
        session.commit()
        session.refresh(employee)

        return employee


def get_employee(employee_id: UUID) -> Employee:
    with Session(engine) as session:
        employee = session.get(Employee, employee_id)

        if employee is None:
            raise ValueError("Сотрудник не найден")

        return employee


def get_employees() -> list[Employee]:
    with Session(engine) as session:
        statement = select(Employee).order_by(Employee.full_name)

        return list(session.exec(statement).all())