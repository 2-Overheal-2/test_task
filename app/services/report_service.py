from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from db import engine
from models import Employee, Request, RequestStatus

def get_requests_count_by_status():
    with Session(engine) as session:
        statement = select(Request.status, func.count(Request.id)).group_by(Request.status).order_by(Request.status)
        result = session.exec(statement).all()

        return result
def get_overdue_requests_count() -> int:
    with Session(engine) as session:
        today = date.today()
        statement = select(func.count(Request.id)).where(Request.due_date < today, Request.status != RequestStatus.DONE)
        result = session.exec(statement).one()

        return result
def get_completed_requests_by_employee() -> list[tuple[str, int]]:
    with Session(engine) as session:
        statement = (
            select(Employee.full_name, func.count(Request.id))
            .join(Request, Request.assigned_to_id == Employee.id)
            .where(Request.status == RequestStatus.DONE)
            .group_by(Employee.id, Employee.full_name)
            .order_by(func.count(Request.id).desc())
        )
        result = session.exec(statement).all()

        return [(full_name, count) for full_name, count in result]
