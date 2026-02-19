import pytest
import pytest_asyncio
import os
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.main import app
from app.db.database import get_db
from dotenv import load_dotenv
from app.models import Base

load_dotenv()

user = os.getenv("DB_USER", "admin")
password = os.getenv("DB_PASSWORD", "admin123")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")

test_db_name = "greendesk_test"

TEST_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{test_db_name}"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback() 
    connection.close()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()