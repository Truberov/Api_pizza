from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import DATABASE_URL


def main():
    engine = create_engine(DATABASE_URL)
    session = Session(bind=engine.connect())
    session.execute("""ALTER TABLE order_dish
                       ADD status VARCHAR(64);""")

    session.close()


if __name__ == "__main__":
    main()

