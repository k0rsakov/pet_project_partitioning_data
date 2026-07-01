import duckdb

con = duckdb.connect()

con.query(
    "ATTACH "
    "'dbname=postgres "
    "user=postgres "
    "host=localhost "
    "password=postgres' "
    "AS db (TYPE postgres, SCHEMA 'public');"
)

con.query(
    """
    INSERT INTO db.orders
    FROM 'orders.parquet' 
    """
)

con.close()
