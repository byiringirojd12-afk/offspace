import os
import tempfile

import pytest
from sqlalchemy import create_engine

# Provide test environment variables before backend imports.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkstemp(suffix='.db')[1]}"
os.environ["OFFSPACE_SECRET_KEY"] = os.environ.get("OFFSPACE_SECRET_KEY", "testsecretkey12345678901234567890")

# Create a temporary SQLite database before importing backend modules so the
# database URL is available when SQLAlchemy engine objects are initialized.
db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.close(db_fd)

from backend.database.models import Base
from backend.database.session import engine

# Ensure the temporary database schema exists for tests.
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    yield

    engine.dispose()
    os.unlink(db_path)
