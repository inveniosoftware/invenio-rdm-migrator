# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL load tests."""

from dataclasses import InitVar, dataclass

import pytest

from invenio_rdm_migrator.load.postgresql import IdentityTableGenerator


@dataclass
class TestModel:
    """Test dataclass model."""

    foo: str
    bar: str
    number: int

    _table_name: InitVar[str] = "test_table"


def test_identity_tg_generate_rows():
    input = {"foo": "some", "bar": "value", "number": 10}
    expected = TestModel(foo="some", bar="value", number=10)

    assert (
        next(IdentityTableGenerator(table=TestModel)._generate_rows(input)) == expected
    )


def test_identity_tg_multiple_tables():
    with pytest.raises(AssertionError):
        IdentityTableGenerator(table=[TestModel, TestModel])
