from datetime import date
import uuid
from services.employee_service import create_employee, get_employee, get_employees

def create_employee_menu() -> None:
    print("\nСоздание сотрудника")

    full_name = input("ФИО: ").strip()
    department_id_raw = input("ID подразделения: ").strip()
    position_id_raw = input("ID должности: ").strip()

    if not full_name:
        print("Ошибка: ФИО не может быть пустым.")
        return
    try:
        department_id = uuid.UUID(department_id_raw)
        position_id = uuid.UUID(position_id_raw)

        employee = create_employee(
            full_name=full_name,
            department_id=department_id,
            position_id=position_id,
        )
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print(f"Сотрудник создан: {employee.id}")


def show_employees_menu() -> None:
    print("\nСписок сотрудников")
    employees = get_employees()

    if not employees:
        print("Сотрудники не найдены.")
        return

    print("\nСписок сотрудников:")
    
    for employee in employees:
        print(
            f"{employee.id} | "
            f"{employee.full_name} | "
            f"department={employee.department_id} | "
            f"position={employee.position_id}"
        )


def employee_menu() -> None:
    while True:
        print("\nСотрудники")
        print("1. Создать сотрудника")
        print("2. Показать сотрудников")
        print("0. Назад")

        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            create_employee_menu()
        elif choice == "2":
            show_employees_menu()
        elif choice == "0":
            return
        else:
            print("Ошибка: неизвестная команда.")