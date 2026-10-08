# Partitioning data / Партиционирование (секционирование) данных

- ✉️ Вопросы, обучение, консультации по Data Engineering — пиши в
  личку: https://korsak0v.notion.site/Data-Engineer-185c62fdf79345eb9da9928356884ea0
- 💥 Аналог Notion (если не работает ссылка выше) — https://www.dataengineers.pro/mentors/korsakov-ivan
- [Видео](https://youtu.be/) — https://youtu.be/

## О видео

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
