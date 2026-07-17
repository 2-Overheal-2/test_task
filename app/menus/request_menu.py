from datetime import date
from unittest import case
import uuid

from models import RequestStatus
from services import request_service


def read_uuid(prompt: str) -> uuid.UUID | None:
    raw_value = input(prompt).strip()

    try:
        return uuid.UUID(raw_value)
    except ValueError:
        print("Ошибка: указан некорректный UUID")
        return None

def read_date(prompt: str) -> date | None:
    raw_value = input(prompt).strip()

    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        print("Ошибка: дата должна быть в формате YYYY-MM-DD")
        return None

def create_request_menu() -> None:
    print("\nСоздание заявки")

    description = input("Описание: ").strip()
    if not description:
        return
    author_id = read_uuid("ID автора: ")
    if author_id is None:
        return
    assignee_id = read_uuid("ID исполнителя: ")
    if assignee_id is None:
        return
    due_date = read_date("Срок выполнения YYYY-MM-DD: ")
    if due_date is None:
            return

    author_id = author_id
    assigned_to_id = assigned_to_id
    due_date = due_date

    request = request_service.create_request(
        description=description,
        author_id=author_id,
        assigned_to_id=assigned_to_id,
        due_date=due_date
    )

    print("\nЗаявка создана")
    print(f"ID: {request.id}")

def change_request_status_menu() -> None:
    print("\nИзменение статуса заявки")

    request_id = read_uuid("ID заявки: ")

    if request_id is None:
        return

    statuses = {
        "1": "NEW",
        "2": "IN_PROGRESS",
        "3": "DONE",
    }

    print("1. NEW")
    print("2. IN_PROGRESS")
    print("3. DONE")

    status_choice = input("Выберите новый статус: ").strip()
    new_status = statuses.get(status_choice)

    if new_status is None:
        print("Ошибка: неизвестный статус.")
        return

    request = request_service.change_status(
            request_id=request_id,
            new_status=new_status
    )


    print(f"Для заявки {request.id} выбран статус {request.status.value}.")


def change_request_assignee_menu() -> None:
    print("\nИзменение исполнителя")

    request_id = read_uuid("ID заявки: ")

    if request_id is None:
        return

    employee_id = read_uuid("ID нового исполнителя: ")

    if employee_id is None:
        return

    request = request_service.change_assignee(
        request_id=request_id,
        assigned_to_id=employee_id,
    )


    print(f"Для заявки {request.id} выбран исполнитель {request.assigned_to_id}.")


def show_requests_menu() -> None:
    print("\nПоиск заявок")
    print("Оставьте поле пустым, чтобы не применять фильтр.")

    status = input("Статус NEW/IN_PROGRESS/DONE: ").strip().upper()
    assigned_to_id = read_uuid("ID исполнителя: ")
    department_id = read_uuid("ID подразделения: ")
    overdue_raw = input("Только просроченные? y/n: ").strip().lower()


    valid_statuses = {"NEW", "IN_PROGRESS", "DONE"}

    if status and status not in valid_statuses:
        print("Ошибка: неизвестный статус.")
        return

    overdue = overdue_raw == "y"

    print("\nПолучены фильтры:")
    print(f"Статус: {status or 'любой'}")
    print(f"Исполнитель: {assigned_to_id or 'любой'}")
    print(f"Подразделение: {department_id or 'любое'}")
    print(f"Только просроченные: {overdue}")

    requests = request_service.get_requests(
        status=RequestStatus(status) if status else None,
        assigned_to_id=assigned_to_id,
        department_id=department_id,
        overdue=overdue,
    )
    for request in requests:
        print(
            request.number,
            request.status.value,
            request.due_date,
            request.description
        )


def request_menu() -> None:
    while True:
        print("\nЗаявки")
        print("1. Создать заявку")
        print("2. Показать заявки")
        print("3. Изменить статус заявки")
        print("4. Изменить исполнителя заявки")
        print("0. Назад")

        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            create_request_menu()
        elif choice == "2":
            show_requests_menu()
        elif choice == "3":
            change_request_status_menu()
        elif choice == "4":
            change_request_assignee_menu()
        elif choice == "0":
            return
        else:
            print("Ошибка: неизвестная команда.")