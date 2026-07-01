import duckdb
import clickhouse_connect

df = duckdb.sql("""
FROM 'orders.parquet'
""").df()


client = clickhouse_connect.get_client(
    host="localhost", port=8123, username="click", password="click"
)

client.insert_df("orders", df)
