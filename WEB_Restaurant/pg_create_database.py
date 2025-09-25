import psycopg2 as pg
from psycopg2 import sql

from settings import config

DATABASE_NAME_CREATE = config.DATABASE_NAME
ROOT_DB_USER = config.ROOT_DB_USER
ROOT_DB_PASSWORD = config.ROOT_DB_PASSWORD

conn = pg.connect(
    dbname="postgres",
    user=ROOT_DB_USER,
    password=ROOT_DB_PASSWORD,
    host="localhost",
    port="5432",
)

conn.autocommit = True  # Включаем автокоммит, иначе CREATE DATABASE не сработает


try:
    # Создаем курсор и выполняем SQL-запрос
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DATABASE_NAME_CREATE))
        )

        print(f"База данних '{DATABASE_NAME_CREATE}' створена!")

except pg.Error as e:
    print("Error connecting or creating database:", e)

finally:
    if conn:
        conn.close()
