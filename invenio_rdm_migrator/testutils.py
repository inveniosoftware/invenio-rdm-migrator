# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Test fixtures and utilities."""

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def db_uri():
    """Database URI."""
    return "postgresql+psycopg://invenio:invenio@localhost:5432/invenio"


@pytest.fixture(scope="session")
def engine(db_uri):
    """SQLAlchemy engine."""
    return sa.create_engine(db_uri)


@pytest.fixture(scope="function")
def session(engine):
    """SQLAlchemy session."""
    conn = engine.connect()
    transaction = conn.begin()

    session = Session(bind=conn, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    conn.close()
