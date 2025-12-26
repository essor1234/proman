import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlmodel import SQLModel

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as pg:
        yield pg

@pytest.fixture(scope="function")
def db_engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url)
    # Import models to create tables
    # from server.account_management_service import models
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)