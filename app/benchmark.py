from __future__ import annotations

import statistics
import time
import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlmodel import Session

from app.database import engine


INDEX_NAME = "idx_request_assignee_status_due_date"
BENCHMARK_RUNS = 10
WARMUP_RUNS = 3


@dataclass
class BenchmarkResult:
    name: str
    timings: list[float]
    explain_plan: list[str]

    @property
    def average_ms(self) -> float:
        return statistics.mean(self.timings)

    @property
    def median_ms(self) -> float:
        return statistics.median(self.timings  )

    @property
    def minimum_ms(self) -> float:
        return min(self.timings)

    @property
    def maximum_ms(self) -> float:
        return max(self.timings)


BENCHMARK_QUERY = text(
    """
    SELECT id, number, description, author_id, assigned_to_id, created_at, due_date, status
    FROM request
    WHERE assigned_to_id = :assigned_to_id AND status = 'IN_PROGRESS' AND due_date < CURRENT_DATE
    ORDER BY due_date;
    """
)


EXPLAIN_QUERY = text(
    """
    EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
    SELECT id, number, status, due_date
    FROM request
    WHERE assigned_to_id = :assigned_to_id AND status = :status
    ORDER BY due_date
    """
)


def get_benchmark_parameters(session: Session) -> tuple[uuid.UUID, str]:
    result = session.execute(
        text(
            """
            SELECT assigned_to_id, status, COUNT(*) AS request_count
            FROM request
            WHERE status = 'IN_PROGRESS' AND due_date < CURRENT_DATE
            GROUP BY assigned_to_id
            ORDER BY COUNT(*) DESC
            LIMIT 1
            """
        )
    ).first()

    if result is None:
        raise RuntimeError(
            "В таблице request нет данных для benchmark"
        )

    print("Параметры benchmark:")
    print(f"Исполнитель: {result.assigned_to_id}")
    print(f"Статус: {result.status}")
    print(
        f"Количество подходящих заявок: "
        f"{result.request_count}"
    )

    return result.assigned_to_id, result.status


def create_benchmark_index(session: Session):
    session.execute(
        text(
            f"""
            CREATE INDEX idx_request_assignee_status_due_date
            ON request (assigned_to_id, status, due_date);
            """
        )
    )
    session.commit()

    print(f"Индекс {INDEX_NAME} создан")


def drop_benchmark_index(session: Session) -> None:
    session.execute(
        text(
            f"""
            DROP INDEX IF EXISTS {INDEX_NAME}
            """
        )
    )
    session.commit()

    print(f"Индекс {INDEX_NAME} удалён")


def execute_benchmark_query(session: Session, *, assigned_to_id: uuid.UUID, status: str) -> float:
    started_at = time.perf_counter()

    result = session.execute(
        BENCHMARK_QUERY,
        {
            "assigned_to_id": assigned_to_id,
            "status": status,
        },
    )

    result.fetchall()

    return (time.perf_counter() - started_at) * 1000


def get_explain_plan(session: Session, *, assigned_to_id: uuid.UUID, status: str) -> list[str]:
    result = session.execute(
        EXPLAIN_QUERY,
        {
            "assigned_to_id": assigned_to_id,
            "status": status,
            "limit": RESULT_LIMIT,
        },
    )

    return [row[0] for row in result.fetchall()]


def measure_query(session: Session, name: str, assigned_to_id: uuid.UUID, status: str) -> BenchmarkResult:

    timing: list[float] = []
    for run_number in range(1, BENCHMARK_RUNS + 1):
        elapsed_ms = execute_benchmark_query(session, assigned_to_id=assigned_to_id, status=status)

        timing.append(elapsed_ms)

        print(f"{name}: запуск {run_number:02d} — {elapsed_ms:.3f} мс")

    return BenchmarkResult(name=name, timings=timing, explain_plan=get_explain_plan(session, assigned_to_id=assigned_to_id, status=status))


def print_benchmark_result(result: BenchmarkResult) -> None:
    print()
    print(result.name)

    print(f"Минимальное время: {result.minimum_ms:.3f} мс")
    print(f"Максимальное время: {result.maximum_ms:.3f} мс")
    print(f"Среднее время: {result.average_ms:.3f} мс")
    print(f"Медианное время: {result.median_ms:.3f} мс")


    for line in result.explain_plan:
        print(line)


def print_comparison(before: BenchmarkResult, after: BenchmarkResult) -> None:
    before_time = before.median_ms
    after_time = after.median_ms

    difference_ms = before_time - after_time

    speedup = (before_time / after_time if after_time > 0 else float("inf"))

    print(f"До индекса:    {before_time:.3f} мс")
    print(f"После индекса: {after_time:.3f} мс")
    print(f"Разница:       {difference_ms:.3f} мс")
    print(f"Ускорение:     {speedup:.2f} раза")



def run_benchmark() -> None:
    with Session(engine) as session:
        assigned_to_id, status = get_benchmark_parameters(session)

        print("Запрос без оптимизации (без индекса)")

        drop_benchmark_index(session)

        before_result = measure_query(session, assigned_to_id=assigned_to_id, status=status)

        print_benchmark_result(before_result)

        print()
        print("Оптимизация с помощью создания индекса")

        create_benchmark_index(session)

        print()

        after_result = measure_query(session, assigned_to_id=assigned_to_id, status=status)

        print_benchmark_result(after_result)

        print_comparison(before=before_result, after=after_result)


if __name__ == "__main__":
    run_benchmark()