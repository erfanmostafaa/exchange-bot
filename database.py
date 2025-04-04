from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
import time
import os


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", default="db")
DB_PORT = os.getenv("DB_PORT", default="5432")

database_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
if database_url:
    engine = create_engine(database_url, echo=True)


def get_db():
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session

def wait_for_db():
    db_connection = False
    while not db_connection:
        try:
            engine = create_engine(database_url)
            with engine.connect() as connection:
                connection.execute(select(1)).scalar_one() 
            db_connection = True
            print("Database is available!")
        except OperationalError:
            print("Database is unavailable, waiting 1 second...")
            time.sleep(1)


if __name__ == "__main__":
    wait_for_db()