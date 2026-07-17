from db import init_db
from menus.employee_menu import employee_menu
from menus.report_menu import report_menu
from menus.request_menu import request_menu
from menus.benchmark_menu import benchmark_menu


def on_startup():
    init_db()



def show_menu() -> None:
    print("Меню:")
    print("1. Сотрудники")
    print("2. Заявки")
    print("3. Отчёты")
    print("4. Benchmark")
    print("0. Выход")


def main() -> None:
    on_startup()
    while True:
        show_menu()
        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            employee_menu()
        elif choice == "2":
            request_menu()
        elif choice == "3":
            report_menu()
        elif choice == "4":
            benchmark_menu()
        elif choice == "0":
            print("Программа завершена")
            break
        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()