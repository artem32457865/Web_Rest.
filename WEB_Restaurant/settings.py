import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

dotenv.load_dotenv()


class DatabaseConfig:
    DATABASE_NAME = os.getenv("DATABASE_NAME", "restaurant_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    ROOT_DB_USER = os.getenv("ROOT_DB_USER")
    ROOT_DB_PASSWORD = os.getenv("ROOT_DB_PASSWORD")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-123")

    def uri_postgres(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DATABASE_NAME}"

    def uri_sqlite(self):
        return f"sqlite:///{self.DATABASE_NAME}.db"


config = DatabaseConfig()

# Змінюємо engine для використання SQLite
engine = create_engine(config.uri_sqlite(), echo=True)  # Використовуємо SQLite
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def create_db(self):
        self.metadata.create_all(engine)

    def drop_db(self):
        self.metadata.drop_all(engine)
