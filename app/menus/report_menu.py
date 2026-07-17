from services.report_service import get_completed_requests_by_employee, get_overdue_requests_count, get_requests_count_by_status


def requests_by_status_report() -> None:
    print("\nКоличество заявок по статусам")

    rows = get_requests_count_by_status()

    for status, count in rows:
        print(f"{status.value}: {count}")

def overdue_requests_report() -> None:

    count = get_overdue_requests_count()

    print(f"\nКоличество просроченных заявок: {count}")


def completed_requests_by_employee_report() -> None:

    rows = get_completed_requests_by_employee()

    print("\nВыполненные заявки по исполнителям")

    if not rows:
        print("Данные отсутствуют")
        return

    for employee_name, count in rows:
        print(f"{employee_name}: {count}")


def report_menu() -> None:
    while True:
        print("\nОтчёты")
        print("1. Количество заявок по статусам")
        print("2. Количество просроченных заявок")
        print("3. Выполненные заявки по исполнителям")
        print("0. Назад")

        choice = input("Выберите отчёт: ").strip()

        
        if choice == "1":
            requests_by_status_report()
        elif choice == "2":
            overdue_requests_report()
        elif choice == "3":
            completed_requests_by_employee_report()
        elif choice == "0":
            return
        else:
            print("Ошибка: неизвестная команда.")