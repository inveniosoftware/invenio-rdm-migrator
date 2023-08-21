# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL transaction load tests."""

from dataclasses import dataclass
from typing import Optional

import pytest
from sqlalchemy.orm import Mapped, mapped_column

from invenio_rdm_migrator.actions import LoadAction, LoadData
from invenio_rdm_migrator.load.postgresql.models import Model
from invenio_rdm_migrator.load.postgresql.transactions import PostgreSQLTx
from invenio_rdm_migrator.load.postgresql.transactions.operations import (
    Operation,
    OperationType,
)


@dataclass
class TransactionData(LoadData):
    """Test load data."""

    id: int
    test: Optional[str] = None


class TestLoadAction(LoadAction):
    """Test load action."""

    name = "test-transaction-load"
    data_cls = TransactionData

    def _generate_rows(self, **kwargs):  # pragma: no cover
        """Yield generated rows."""
        op_type = OperationType.INSERT
        if not self.data.test:
            op_type = OperationType.DELETE
        elif "update" in self.data.test:
            op_type = OperationType.UPDATE

        yield Operation(
            type=op_type,
            model=TestModel,
            data={"id": self.data.id, "test": self.data.test},
        )


class TestModel(Model):
    """Persistent identifier dataclass model."""

    __tablename__ = "transaction-test"

    id: Mapped[int] = mapped_column(primary_key=True)
    test: Mapped[str]


@pytest.fixture(scope="module")
def database(engine):
    tables = [TestModel]

    # create tables
    for model in tables:
        model.__table__.create(bind=engine, checkfirst=True)

    yield engine

    # remove tables
    for model in tables:
        model.__table__.drop(engine)


@pytest.fixture(scope="function")
def test_item(database, session):
    obj = TestModel(id=1, test="test item")
    session.add(obj)
    session.commit()


@pytest.fixture(scope="function")
def pg_tx(db_uri, session):
    return PostgreSQLTx(db_uri=db_uri, _session=session)


###
# Operation Type
###


def test_load_transaction_insert(session, pg_tx, database):
    tx = [TestLoadAction(data={"tx_id": 1, "id": 101, "test": "insert test"})]
    pg_tx.run(tx)

    result = session.query(TestModel).all()
    assert len(result) == 1
    assert result[0].id == 101
    assert result[0].test == "insert test"

    # suboptimal but pragmatic cleanup
    session.delete(result[0])
    session.commit()


def test_load_transaction_delete(pg_tx, session, database, test_item):
    tx = [TestLoadAction(data={"tx_id": 2, "id": 1})]
    pg_tx.run(tx)

    session.query(TestModel).all()


def test_load_transaction_update(pg_tx, session, database, test_item):
    tx = [TestLoadAction(data={"tx_id": 1, "id": 1, "test": "update test"})]
    pg_tx.run(tx)

    result = session.query(TestModel).all()
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].test == "update test"


# ###
# # Transaction cardinality
# ###


def test_load_no_transaction(pg_tx, session, database):
    pg_tx.run([])

    result = session.query(TestModel).all()
    assert len(result) == 0


def test_load_transaction_multiple_actions(pg_tx, session, database):
    tx = [
        TestLoadAction(data={"tx_id": 1, "id": 101, "test": "first instance"}),
        TestLoadAction(data={"tx_id": 2, "id": 102, "test": "second instance"}),
    ]
    pg_tx.run(tx)

    result = session.query(TestModel).all()
    assert len(result) == 2
    assert result[0].id == 101
    assert result[0].test == "first instance"
    assert result[1].id == 102
    assert result[1].test == "second instance"
