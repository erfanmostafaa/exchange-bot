import time
from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError
from decouple import config


POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_DB = config("POSTGRES_DB")
DB_HOST = config("DB_HOST", default="db")
DB_PORT = config("DB_PORT", default="5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

def wait_for_db():
    db_connection = False
    while not db_connection:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                connection.execute(select(1)).scalar_one() 
            db_connection = True
            print("Database is available!")
        except OperationalError:
            print("Database is unavailable, waiting 1 second...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()

