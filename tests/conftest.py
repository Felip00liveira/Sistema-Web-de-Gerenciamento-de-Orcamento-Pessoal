import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_db
from fast_zero.models import mapeador


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    mapeador.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    mapeador.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def override_get_db():
        return session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()