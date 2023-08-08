# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL bulk load tests."""

import tempfile
from dataclasses import InitVar
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Mapped, mapped_column

from invenio_rdm_migrator.load.postgresql.bulk import PostgreSQLCopyLoad
from invenio_rdm_migrator.load.postgresql.bulk.generators import (
    ExistingDataTableGenerator,
    SingleTableGenerator,
)
from invenio_rdm_migrator.load.postgresql.models import Model


@pytest.fixture(scope="function")
def data_dir():
    """Yields a temporary directory."""
    data_dir = tempfile.TemporaryDirectory()
    yield data_dir
    data_dir.cleanup()


###
#  Table Generators
###


class TestModel(Model):
    """Test dataclass model."""

    foo: Mapped[str]
    bar: Mapped[str]
    number: Mapped[int] = mapped_column(primary_key=True)

    __tablename__: InitVar[str] = "test_table"


def test_identity_tg_generate_rows():
    input = {"foo": "some", "bar": "value", "number": 10}
    expected = TestModel(foo="some", bar="value", number=10)

    assert next(SingleTableGenerator(table=TestModel)._generate_rows(input)) == expected


def test_identity_tg_multiple_tables():
    with pytest.raises(AssertionError):
        SingleTableGenerator(table=[TestModel, TestModel])


###
# Existing data
###


class TestModelToo(Model):
    """Another dataclass model."""

    foo: Mapped[str]
    bar: Mapped[str]
    number: Mapped[int] = mapped_column(primary_key=True)

    __tablename__: InitVar[str] = "test_table_too"


class CopyLoad(PostgreSQLCopyLoad):
    """Mock load class."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                ExistingDataTableGenerator(tables=[TestModelToo]),
                SingleTableGenerator(table=TestModel),
            ],
            **kwargs
        )


@pytest.fixture(scope="function")
def entries():
    return [{"foo": "test", "bar": "also testing", "number": 1}]


def mock_load(_, table_entries):
    """Mock method to assert the iterators content.

    Otherwise the assert would check memory addresses which do not match.
    """
    assert list(table_entries) == [(True, TestModelToo), (True, TestModel)]


@patch.object(CopyLoad, "_load", mock_load)
@patch.object(CopyLoad, "_post_load")  # needs mocking due to db connection
@patch.object(ExistingDataTableGenerator, "prepare")
@patch.object(SingleTableGenerator, "prepare")
def test_load_with_all_existing_data(
    m_prepare_i, m_prepare_ii, _, data_dir, tmp_dir, entries
):
    """Checks the load does not call prepare on the tg (i.e. no data written)."""
    load = CopyLoad(
        db_uri=None, data_dir=data_dir.name, tmp_dir=tmp_dir.name, existing_data=True
    )
    load.run(entries)

    # the table generators prepare step (write csv files) were not called
    m_prepare_i.assert_not_called()
    m_prepare_ii.assert_not_called()

    # check the load would be done with all existing data is done via mock_load


def mock_load(_, table_entries):
    """Mock method to assert the iterators content.

    Otherwise the assert would check memory addresses which do not match.
    """
    # note the second item on the list has a False as existing_data
    assert list(table_entries) == [(True, TestModelToo), (False, TestModel)]


@patch.object(CopyLoad, "_load", mock_load)
@patch.object(CopyLoad, "_post_load")  # needs mocking due to db connection
@patch.object(ExistingDataTableGenerator, "_generate_rows")
@patch.object(SingleTableGenerator, "_generate_rows")
def test_load_with_existing_data_tg(
    m_gen_rows_i, m_gen_rows_ii, _, data_dir, tmp_dir, entries
):
    """Checks the load calls prepare on one tg."""
    load = CopyLoad(db_uri=None, data_dir=data_dir.name, tmp_dir=tmp_dir.name)
    load.run(entries)

    # the `prepare` method is called on both tg, however the filtering happens at tg level
    # therefore we assert on row generation (could also be done on pk or refs)
    m_gen_rows_i.assert_called()
    m_gen_rows_ii.assert_not_called()  # not called

    # check the load would be done with all existing data is done via mock_load


class CopyLoadToo(PostgreSQLCopyLoad):
    """Mock load class."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                SingleTableGenerator(table=TestModelToo),
                SingleTableGenerator(table=TestModel),
            ],
            **kwargs
        )


def mock_load(_, table_entries):
    """Mock method to assert the iterators content.

    Otherwise the assert would check memory addresses which do not match.
    """
    assert list(table_entries) == [(False, TestModelToo), (False, TestModel)]


@patch.object(CopyLoadToo, "_load", mock_load)
@patch.object(CopyLoadToo, "_post_load")  # needs mocking due to db connection
@patch.object(SingleTableGenerator, "_generate_rows")
def test_load_without_existing_data(m_gen_rows, _, data_dir, tmp_dir, entries):
    """Checks the load calls prepare on both tg."""

    load = CopyLoadToo(db_uri=None, data_dir=data_dir.name, tmp_dir=tmp_dir.name)
    load.run(entries)

    # the `prepare` method is called on both tg, however the filtering happens at tg level
    # therefore we assert on row generation (could also be done on pk or refs)
    m_gen_rows.call_count = 2

    # check the load would be done with all existing data is done via mock_load
