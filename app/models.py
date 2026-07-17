from enum import Enum
import uuid
from datetime import UTC, datetime, date
from sqlmodel import SQLModel, Field
from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DepartmentBase(SQLModel):
    name: str

class Department(DepartmentBase, table=True):
    __tablename__ = "department"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
class PositionBase(SQLModel):
    name: str = Field(max_length=255, unique=True)

class Position(PositionBase, table=True):
    __tablename__ = "position"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class EmployeeBase(SQLModel):
    full_name: str = Field(max_length=255)
    department_id: uuid.UUID = Field(foreign_key="department.id")
    position_id: uuid.UUID = Field(foreign_key="position.id")
    
class Employee(EmployeeBase, table=True):
    __tablename__ = "employee"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class RequestStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class RequestBase(SQLModel):
    number: str = Field(
        index=True,
        unique=True,
        max_length=30,
    )
    description: str
    author_id: uuid.UUID = Field(foreign_key="employee.id")
    assigned_to_id: uuid.UUID = Field(foreign_key="employee.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    due_date: date
    status: RequestStatus = Field(default=RequestStatus.NEW)

class Request(RequestBase, table=True):
    __tablename__ = "request"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)