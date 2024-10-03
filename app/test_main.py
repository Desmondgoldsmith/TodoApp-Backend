import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .main import app, get_db
from .database import Base
from . import models
import os
from dotenv import load_dotenv

load_dotenv()

# Test database configuration
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_todos_db")
TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "your_password")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")

# Create a test database URL
TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Create a test engine
engine = create_async_engine(TEST_DATABASE_URL, echo=True)

# Create a test session
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency override
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Fixture to create and drop test database tables
@pytest.fixture(scope="module")
async def create_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture for test client
@pytest.fixture(scope="module")
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Test cases
@pytest.mark.asyncio
async def test_create_todo(create_test_database, test_client):
    response = await test_client.post(
        "/create_todo",
        json={"title": "Test Todo", "description": "This is a test todo", "completed": False}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo"
    assert data["completed"] == False
    assert "id" in data

@pytest.mark.asyncio
async def test_get_todos(create_test_database, test_client):
    response = await test_client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_get_one_todo(create_test_database, test_client):
    # First, create a todo
    create_response = await test_client.post(
        "/create_todo",
        json={"title": "Test Todo", "description": "This is a test todo", "completed": False}
    )
    created_todo = create_response.json()

    # Now, get the todo by id
    response = await test_client.get(f"/todo/{created_todo['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_todo["id"]
    assert data["title"] == created_todo["title"]

@pytest.mark.asyncio
async def test_update_todo(create_test_database, test_client):
    # First, create a todo
    create_response = await test_client.post(
        "/create_todo",
        json={"title": "Test Todo", "description": "This is a test todo", "completed": False}
    )
    created_todo = create_response.json()

    # Now, update the todo
    update_response = await test_client.put(
        f"/update_todo/{created_todo['id']}",
        json={"title": "Updated Todo", "description": "This is an updated todo", "completed": True}
    )
    assert update_response.status_code == 201
    updated_todo = update_response.json()
    assert updated_todo["id"] == created_todo["id"]
    assert updated_todo["title"] == "Updated Todo"
    assert updated_todo["completed"] == True

@pytest.mark.asyncio
async def test_delete_todo(create_test_database, test_client):
    # First, create a todo
    create_response = await test_client.post(
        "/create_todo",
        json={"title": "Test Todo", "description": "This is a test todo", "completed": False}
    )
    created_todo = create_response.json()

    # Now, delete the todo
    delete_response = await test_client.delete(f"/delete_todo/{created_todo['id']}")
    assert delete_response.status_code == 204

    # Try to get the deleted todo (should return 404)
    get_response = await test_client.get(f"/todo/{created_todo['id']}")
    assert get_response.status_code == 404