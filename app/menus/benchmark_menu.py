def run_request_benchmark() -> None:
    print("\nBenchmark выборки заявок")

    # Позже:
    #
    # result = benchmark_service.measure_overdue_requests_query()
    #
    # print(f"Количество строк: {result.rows_count}")
    # print(f"Время выполнения: {result.elapsed_seconds:.6f} сек.")

    print("Benchmark пока не подключён.")


def benchmark_menu() -> None:
    while True:
        print("\nBenchmark")
        print("1. Замерить время выполнения запроса")
        print("0. Назад")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            run_request_benchmark()
        elif choice == "0":
            return
        else:
            print("Ошибка: неизвестная команда.")