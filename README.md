# Employee Requests

Консольное приложение для управления сотрудниками, подразделениями, должностями и заявками.

Использованные технологии:

* Python
* SQLModel
* PostgreSQL
* Alembic
* Docker Compose
* Faker

## Требования

Для запуска проекта необходимо установить:

* Docker
* Docker Compose
* Git

Проверить установку можно командами:

```bash
docker --version
docker compose version
git --version
```

## Клонирование проекта

```bash
git clone https://github.com/2-Overheal-2/test_task.git
cd test_task
```


## Запуск компоуза

Запустите docer compose:

```bash
docker compose up -d --build
```

Проверить состояние:

```bash
docker compose ps
```

Контейнер базы данных должен находиться в состоянии `healthy`.

## Заполнение базы тестовыми данными

При запуске контейнера миграции выполняются автоматически

Для генерации тестовых данных выполните:

```bash
docker compose run --rm app python seed.py
```

Скрипт создаёт:

* 20 подразделений
* 50 должностей
* 1000 сотрудников
* 1 000 000 заявок

## Запуск консольного приложения

После заполнение таблиц:

```bash
docker compose run --rm app python main.py
```

## Повторный запуск

Если база данных уже создана и заполнена, достаточно выполнить:

```bash
docker compose run --rm app python main.py
```

## Остановка проекта

Остановить контейнеры:

```bash
docker compose down
```

Остановить контейнеры и удалить временные контейнеры проекта:

```bash
docker compose down --remove-orphans
```

## Полное удаление базы данных

Для удаления контейнеров вместе с томом PostgreSQL выполните:

```bash
docker compose down -v
```

Команда удалит все данные базы. После неё потребуется повторно применить миграции и запустить `seed.py`.

Файлы миграций должны храниться в каталоге:

```text
app/alembic/versions/
```

## Запуск теста производительности

Для запуска benchmark-скрипта выполните:

```bash
docker compose run --rm app python benchmark.py
```

Тест используется для анализа производительности запросов к таблице заявок.

## Архитектура

* `menus` отвечает за взаимодействие с пользователем;
* `services` содержит бизнес-логику;
* `repositories` отвечает за работу с базой данных;
* `models.py` содержит SQLModel-модели;
* `db.py` содержит настройки подключения к базе данных;
* `alembic` содержит миграции;
* `seed.py` генерирует тестовые данные;
* `benchmark.py` проверяет производительность запросов.

## Описание реализованного бизнес-процесса

Приложение моделирует процесс обработки внутренних заявок организации.

Сотрудники создают заявки, которые содержат описание, срок выполнения, приоритет и текущий статус. Каждая заявка может быть назначена конкретному исполнителю.
Исполнитель изменяет статус заявки по мере выполнения работы, а система позволяет отслеживать просроченные заявки, фильтровать их по различным критериям
и получать статистические отчёты.

## Реализованные бизнес-правила

В приложении реализованы следующие правила:

* каждый сотрудник принадлежит одному подразделению
* каждый сотрудник занимает одну должность
* заявка может иметь только одного назначенного исполнителя
* каждая заявка имеет один из статусов:

  * `NEW`
  * `IN_PROGRESS`
  * `DONE`
  
* заявки могут фильтроваться по исполнителю, статусу и признаку просроченности

## Оптимизация базы данных

Для повышения производительности поиска заявок был проанализирован следующий запрос:

```sql
SELECT id, number, description, author_id, assigned_to_id, created_at, due_date, status
FROM request
WHERE assigned_to_id = :assigned_to_id AND status = 'IN_PROGRESS' AND due_date < CURRENT_DATE
ORDER BY due_date;
```

Для данного запроса был создан составной индекс:

```sql
CREATE INDEX idx_request_assignee_status_due_date
ON request (assigned_to_id, status, due_date);
```

Такой индекс позволяет PostgreSQL значительно сократить количество просматриваемых строк при поиске заявок конкретного исполнителя с определённым статусом
и сортировкой по сроку выполнения.
Производительность оценивалась на базе данных, содержащей около 1 000 000 записей в таблице `request`, с помощью скрипта `benchmark.py`,
который измеряет время выполнения запроса до и после создания индекса.

Логи результата:
```
Параметры benchmark:
Исполнитель: 072e7df7-c77e-46c5-9346-87df936db257
Статус: IN_PROGRESS
Количество подходящих заявок: 359
Запрос без оптимизации (без индекса)
Индекс idx_request_assignee_status_due_date удалён
Замер: 01 — 106.200 мс
Замер: 02 — 75.608 мс
Замер: 03 — 70.182 мс
Замер: 04 — 71.080 мс
Замер: 05 — 67.770 мс
Замер: 06 — 68.571 мс
Замер: 07 — 68.028 мс
Замер: 08 — 70.044 мс
Замер: 09 — 67.912 мс
Замер: 10 — 68.349 мс

Минимальное время: 67.770 мс
Максимальное время: 106.200 мс
Среднее время: 73.375 мс
Медианное время: 69.308 мс
Gather Merge  (cost=52721.93..52754.13 rows=276 width=30) (actual time=60.598..64.398 rows=388 loops=1)
  Workers Planned: 2
  Workers Launched: 2
  Buffers: shared hit=6183 read=39398
  ->  Sort  (cost=51721.90..51722.25 rows=138 width=30) (actual time=56.297..56.305 rows=129 loops=3)
        Sort Key: due_date
        Sort Method: quicksort  Memory: 32kB
        Buffers: shared hit=6183 read=39398
        Worker 0:  Sort Method: quicksort  Memory: 31kB
        Worker 1:  Sort Method: quicksort  Memory: 31kB
        ->  Parallel Seq Scan on request  (cost=0.00..51717.00 rows=138 width=30) (actual time=1.146..55.821 rows=129 loops=3)
              Filter: ((assigned_to_id = '072e7df7-c77e-46c5-9346-87df936db257'::uuid) AND (status = 'IN_PROGRESS'::requeststatus))
              Rows Removed by Filter: 333204
              Buffers: shared hit=6069 read=39398
Planning Time: 0.078 ms
Execution Time: 64.463 ms

Оптимизация с помощью создания индекса
Индекс idx_request_assignee_status_due_date создан

Замер: 01 — 6.377 мс
Замер: 02 — 5.956 мс
Замер: 03 — 5.451 мс
Замер: 04 — 5.913 мс
Замер: 05 — 5.258 мс
Замер: 06 — 5.142 мс
Замер: 07 — 5.917 мс
Замер: 08 — 5.315 мс
Замер: 09 — 5.173 мс
Замер: 10 — 5.903 мс

Минимальное время: 5.142 мс
Максимальное время: 6.377 мс
Среднее время: 5.640 мс
Медианное время: 5.677 мс
Sort  (cost=1266.29..1267.12 rows=331 width=30) (actual time=0.940..0.971 rows=388 loops=1)
  Sort Key: due_date
  Sort Method: quicksort  Memory: 46kB
  Buffers: shared hit=391
  ->  Bitmap Heap Scan on request  (cost=11.82..1252.44 rows=331 width=30) (actual time=0.288..0.749 rows=388 loops=1)
        Recheck Cond: ((assigned_to_id = '072e7df7-c77e-46c5-9346-87df936db257'::uuid) AND (status = 'IN_PROGRESS'::requeststatus))
        Heap Blocks: exact=386
        Buffers: shared hit=391
        ->  Bitmap Index Scan on idx_request_assignee_status_due_date  (cost=0.00..11.74 rows=331 width=0) (actual time=0.219..0.219 rows=388 loops=1)
              Index Cond: ((assigned_to_id = '072e7df7-c77e-46c5-9346-87df936db257'::uuid) AND (status = 'IN_PROGRESS'::requeststatus))
              Buffers: shared hit=5
Planning Time: 0.088 ms
Execution Time: 1.080 ms
До индекса:    69.308 мс
После индекса: 5.677 мс
Разница:       63.631 мс
```
В результате использования составного индекса время выполнения запроса существенно сократилось за счёт отказа от полного сканирования таблицы и использования индексного поиска.


