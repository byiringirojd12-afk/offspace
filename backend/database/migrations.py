from sqlalchemy import create_engine
from backend.database.models import Base
from backend.database.session import DATABASE_URL


def run_migrations() -> None:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    run_migrations()
    print("Database schema created.")
