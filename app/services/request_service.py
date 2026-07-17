from datetime import date
from uuid import UUID, uuid4

from sqlmodel import Session, select
from sqlalchemy import text
from db import engine
from models import Employee, Request, RequestStatus


ALLOWED_STATUS_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.NEW: {RequestStatus.IN_PROGRESS},
    RequestStatus.IN_PROGRESS: {RequestStatus.DONE},
    RequestStatus.DONE: set(),
}


def generate_request_number(session: Session) -> int:
    result = session.exec(text("SELECT nextval('request_number_seq')"))

    return result.one()


def create_request(description: str, author_id: UUID, assigned_to_id: UUID,due_date: date):
    description = description.strip()

    if not description:
        raise ValueError("Описание запроса не может быть пустым")

    with Session(engine) as session:
        author = session.get(Employee, author_id)

        if author is None:
            raise ValueError("Автор не найден")

        assigned_to = session.get(Employee, assigned_to_id)

        if assigned_to is None:
            raise ValueError("Исполнитель не найден")
        
        due_date = due_date

        request = Request(
            number=generate_request_number(),
            description=description,
            author_id=author_id,
            assigned_to_id=assigned_to_id,
            due_date=due_date
        )

        session.add(request)
        session.commit()
        session.refresh(request)

        return request


def change_request_status(request_id: UUID, new_status: RequestStatus):
    with Session(engine) as session:

        request = session.get(Request, request_id)

        if request is None:
            raise ValueError("Заявка не найдена")

        if new_status not in ALLOWED_STATUS_TRANSITIONS.get(request.status, set()):
            raise ValueError("Недопустимый переход статуса ", f"{request.status.value} -> {new_status.value}")

        request.status = new_status
        session.commit()
        session.refresh(request)

        return request


def get_requests(status: RequestStatus | None = None, assigned_to_id: UUID | None = None, department_id: UUID | None = None, overdue: bool = False,) -> list[Request]:
    with Session(engine) as session:
        statement = select(Request)

        if department_id is not None:
            statement = statement.where(Request.department_id == department_id)
        if status is not None:
            statement = statement.where(Request.status == status)
        if assigned_to_id is not None:
            statement = statement.where(Request.assigned_to_id == assigned_to_id)
        if overdue:
            statement = statement.where(Request.due_date < date.today(), Request.status != RequestStatus.DONE)
        
        statement = statement.order_by(Request.due_date, Request.created_at)

        return list(session.exec(statement).all())