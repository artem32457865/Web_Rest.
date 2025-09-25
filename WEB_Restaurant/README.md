# Online Restauran

Oлайн-ресторан, у якому відвідувачі зможуть переглядати
меню, обирати смачні страви та оформлювати замовлення прямо на сайті. __Користувачі__ зможуть зареєструватися, заходити до своїх акаунтів, бачити історію замовлень, а __адміністратор__ – керувати меню, додаючи нові, апетитні позиції.



## create .env

    DB_USER = <postgres_user>
    DB_PASSWORD = <postgres_passw>
    DATABASE_NAME = "restaurant_db"


    ROOT_DB_USER = "your_postgres_user"
    ROOT_DB_PASSWORD = "your_pg_pass"

    SECRET_KEY = "secret_key"           # os.urandom(32).hex()

## create database

1) **Postgres**: 
```
python3 pg_create_database.py
```


## Необхідні бібліотеки:
 - Flask
 - SQLAlchemy
 - Flask-Login
 - Flask-WTF
 - psycopg2
 - Flask-Caching

`pip install -r requirements.txt`

## Запуск проекту

```
python3 app.py
``` 