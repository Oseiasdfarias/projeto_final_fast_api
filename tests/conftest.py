import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fast_api_madr.app import app
from fast_api_madr.database import get_session
from fast_api_madr.models import Account, table_registry
from fast_api_madr.security import get_password_hash


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    username = factory.Sequence(lambda n: f"test{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}+senha")


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:16", driver="psycopg") as prostgres:
        _engine = create_engine(prostgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def account(session):
    pwd = "testtest"
    account = AccountFactory(password=get_password_hash(pwd))

    session.add(account)
    session.commit()
    session.refresh(account)

    account.clean_password = pwd  # Monkey Patch

    return account


@pytest.fixture
def other_account(session):
    account = AccountFactory()
    session.add(account)
    session.commit()
    session.refresh(account)

    return account


@pytest.fixture
def token(client, account):
    response = client.post(
        "/auth/token",
        data={"username": account.email, "password": account.clean_password},
    )
    return response.json()["access_token"]
