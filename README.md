# Partitioning data / Партиционирование (секционирование) данных

- ✉️ Вопросы, обучение, консультации по Data Engineering — пиши в
  личку: https://korsak0v.notion.site/Data-Engineer-185c62fdf79345eb9da9928356884ea0
- 💥 Аналог Notion (если не работает ссылка выше) — https://www.dataengineers.pro/mentors/korsakov-ivan
- [Видео](https://youtu.be/zYbTBGPlMYU) — https://youtu.be/zYbTBGPlMYU

## О видео

🔥 Как правильно партиционировать таблицы в PostgreSQL и ClickHouse? Разбираемся на практике, как выбрать ключ партиционирования, что происходит с запросами и какие нюансы важно учитывать Data Engineer.

В этом видео на реальном примере разберём партиционирование данных: от анализа исходных данных и выбора ключа до реализации в PostgreSQL и ClickHouse. Посмотрим на планы выполнения запросов, сравним поведение партиционированных и обычных таблиц и обсудим, в каких задачах партиционирование действительно полезно.

💡 Партиционирование — это не только про ускорение запросов. Оно также помогает управлять жизненным циклом данных: удалять старые данные, настраивать TTL, архивировать холодные данные и эффективнее использовать хранилище.

В видео покажу:
- как проанализировать данные и выбрать ключ партиционирования;
- почему важно учитывать реальные запросы и распределение данных;
- как создать партиционированную таблицу в PostgreSQL;
- что такое DEFAULT partition и какие нюансы нужно учитывать при добавлении новых партиций;
- как проверить partition pruning в планах выполнения запросов;
- как партиционировать таблицы в ClickHouse;
- как посмотреть информацию о партициях через system.parts в ClickHouse;
- чем отличаются планы выполнения запросов для партиционированных и обычных таблиц;
- когда партиционирование полезно для удаления, архивирования и хранения данных;
- какие ошибки и ограничения стоит учитывать при проектировании.

📦 Код проекта и примеры из видео:
https://github.com/k0rsakov/pet_project_partitioning_data

✉️ Вопросы, обучение и консультации по Data Engineering — пиши:
https://korsak0v.notion.site/Data-Engineer-185c62fdf79345eb9da9928356884ea0

💥 Альтернативная ссылка на менторство:
https://www.dataengineers.pro/mentors/korsakov-ivan

Мои соцсети и полезные ссылки:
- Менторство по Data Engineering — https://korsak0v.notion.site/Data-Engineer-185c62fdf79345eb9da9928356884ea0
- TG-канал — https://t.me/DataLikeQWERTY
- Instagram — https://www.instagram.com/i__korsakov/
- Habr — https://habr.com/ru/users/k0rsakov/publications/articles/

Таймкоды:
- 00:00 — Начало
- 01:37 — Разбор модели данных и генерация данных
- 03:48 — Разбор и анализ сгенерированных данных
- 05:43 — Что такое партиция на физическом примере
- 06:50 — Как выбрать ключ для партиционирования
- 09:09 — Анализ дат для выбора верного ключа партиционирования
- 12:37 — Анализ списков (перечислений) для выбора верного ключа партиционирования
- 14:05 — Резюме по анализу данных и партиций
- 14:53 — Разбор и объяснение инфраструктуры
- 15:55 — Изучение партиций (секций) на базе PostgreSQL
- 16:23 — Разбор и объяснение DDL партиционированной таблицы в PostgreSQL
- 18:26 — Разбор и объяснение как работает default партиция (секция) в PostgreSQL
- 20:00 — Рассмотрение партиционированной таблицы в PostgreSQL
- 20:53 — Разбор и объяснение планов запроса в PostgreSQL для партиционированной таблицы
- 25:19 — Разбор и объяснение работы не партиционированной таблицы в PostgreSQL
- 26:26 — Изучение партиций (секций) на базе ClickHouse
- 26:55 — Разбор и объяснение DDL партиционированной таблицы в ClickHouse
- 28:02 — Наполнение таблицы в ClickHouse
- 28:30 — Разбор и объяснение планов запроса в ClickHouse для партиционированной таблицы
- 31:52 — Разбор и объяснение работы не партиционированной таблицы в ClickHouse
- 32:55 — Рекомендации, советы и информация на подумать
- 40:54 — Резюме и подведение итогов

#dataengineering #dataengineer #postgresql #clickhouse #sql #базыданных #партиционирование #partitioning #аналитикаданных #хранилищеданных #petproject #разработчик

## О проекте

Запуск виртуального окружения для работы:

```bash
uv sync
```

Запуск `jupyter lab` через `uv`:

```bash
uv run jupyter lab
```

Для запуска контейнеров с PostgreSQL и ClickHouse, выполните команду:

```bash
docker-compose up -d
```

### Как воссоздать демо-стенд

1) Создать виртуальное окружение через `uv`
2) Выполнить код [init_orders_parquet.py](init_orders_parquet.py)
    - Можете параметризировать его самостоятельно
3) Поднять инфраструктуру
4) Создать подключение к БД через DBeaver или другой обозреватель
5) Выполнить DDL команды в каждой из БД на основании имени:
    - В PostgreSQL — [DDL_PG.sql](sql_ddl/DDL_PG.sql)
    - В ClickHouse — [DDL_CH.sql](sql_ddl/DDL_CH.sql)
6) У вас будут созданы все таблицы необходимые для исследования
7) Выполнить DML код для каждой из БД на основании имени:
    - Для PostgreSQL — [init_orders_pg.py](init_orders_pg.py)
    - Для ClickHouse — [init_orders_ch.py](init_orders_ch.py)
8) У вас будет заполнена таблица `orders` в каждой из БД на основании
   скрипта [init_orders_parquet.py](init_orders_parquet.py)

## Полезные ссылки

- [Northwind ER](https://github.com/pthom/northwind_psql/blob/master/ER.png)
  - [Как запустить базу данных для обучения. Практическое видео на PostgreSQL](https://youtu.be/NFJbDist6Do)
- PostgreSQL
  - [Postgres EXPLAIN Visualizer (tatiyants)](http://tatiyants.com/pev/#/plans)
  - [5.11. Секционирование таблиц](https://postgrespro.ru/docs/postgresql/16/ddl-partitioning?lang=ru)
- ClickHouse
  - [ClickHouse table partitions](https://clickhouse.com/docs/concepts/core-concepts/partitions)
  - [Custom Partitioning Key](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/custom-partitioning-key)
  - [system.parts](https://clickhouse.com/docs/reference/system-tables/parts)
  - [How can I do partitioned writes by year and month on S3?](https://clickhouse.com/docs/resources/support-center/knowledge-base/data-import-export/s3-export-data-year-month-folders)
  - [External disks for storing data](https://clickhouse.com/docs/concepts/features/configuration/server-config/storing-data)
