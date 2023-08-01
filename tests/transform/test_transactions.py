# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity transaction transformation tests."""

from dataclasses import dataclass

import pytest

from invenio_rdm_migrator.actions import LoadAction, LoadData, TransformAction
from invenio_rdm_migrator.extract import Tx
from invenio_rdm_migrator.transform import BaseTxTransform
from invenio_rdm_migrator.transform.errors import MultipleActionMatches, NoActionMatch


@pytest.fixture()
def tx(scope="function"):
    return Tx(
        id=1,
        operations=[
            {
                "table": "records",
                "op": "I",
                "after": {"id": "abc", "json": {"title": "Test title"}},
            },
            {"table": "files", "op": "I", "after": {"key": "data.zip"}},
            {"table": "files", "op": "I", "after": {"key": "article.pdf"}},
            {"table": "files", "op": "I", "after": {"key": "figure.png"}},
        ],
    )


@dataclass
class TestLoadData(LoadData):
    record: dict
    files: list[dict]


class TestLoadAction(LoadAction):
    """Test load action."""

    name = "test-load"

    data_cls = TestLoadData

    def _generate_rows(self, **kwargs):  # pragma: no cover
        """Yield generated rows."""
        yield


class TestTransformAction(TransformAction):
    """Test transform action."""

    name = "test-transform"
    load_cls = TestLoadAction

    @classmethod
    def matches_action(cls, tx: Tx):  # pragma: no cover
        """Checks if the data matches with that required by the action."""
        record_ops = [
            o for o in tx.operations if o["table"] == "records" and o["op"] == "I"
        ]
        has_one_record_insert = len(record_ops) == 1
        has_files_insert = any(
            o for o in tx.operations if o["table"] == "files" and o["op"] == "I"
        )
        return has_one_record_insert and has_files_insert

    def _transform_data(self):  # pragma: no cover
        """Transforms the data and returns an instance of the ``data_cls``."""
        record = next(o["after"] for o in self.tx.operations if o["table"] == "records")
        record["json"]["titles"] = [record["json"].pop("title")]
        return dict(
            tx_id=self.tx.id,
            record=record,
            files=[o["after"] for o in self.tx.operations if o["table"] == "files"],
        )


class TestTxTransform(BaseTxTransform):
    actions = [
        TestTransformAction,
    ]


def test_transform_returns_load_action(tx):
    transform = TestTxTransform()
    load_action = transform._transform(tx)
    assert isinstance(load_action, TestLoadAction)
    assert isinstance(load_action.data, TestLoadData)
    assert load_action.data.tx_id == 1
    assert load_action.data.record == {"id": "abc", "json": {"titles": ["Test title"]}}
    assert load_action.data.files == [
        # NOTE: Order doesn't really matter here
        {"key": "data.zip"},
        {"key": "article.pdf"},
        {"key": "figure.png"},
    ]


def test_multiple_action_matches(tx):
    class MultipleTxTransform(BaseTxTransform):
        actions = [
            TestTransformAction,
            TestTransformAction,
        ]

    transform = MultipleTxTransform()
    with pytest.raises(MultipleActionMatches):
        transform._transform(tx)


def test_no_action_matches():
    tx = Tx(
        id=1,
        operations=[
            {"table": "random", "op": "I", "after": {"some": "value"}},
        ],
    )
    transform = TestTxTransform()
    with pytest.raises(NoActionMatch):
        transform._transform(tx)
