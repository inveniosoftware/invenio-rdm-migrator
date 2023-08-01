# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Draft actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions import DraftCreateAction
from invenio_rdm_migrator.streams.models.files import FilesBucket
from invenio_rdm_migrator.streams.models.pids import PersistentIdentifier
from invenio_rdm_migrator.streams.models.records import (
    RDMDraftMetadata,
    RDMParentMetadata,
    RDMVersionState,
)


@pytest.fixture(scope="function")
def draft_data():
    """Draft data."""
    return {
        "id": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "json": {
            "id": "1217215",
            "$schema": "https://zenodo.org/schemas/deposits/records/record-v1.0.0.json",
            "pids": {},
            "files": {"enabled": True},
            "metadata": {},
            "access": {
                "record": "public",
                "files": "public",
            },
            "custom_fields": {},
        },
        "version_id": 1,
        "index": 1,
        "bucket_id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "parent_id": "9493793c-47d2-48e2-9867-ca597b4ebb41",
        "expires_at": None,
        "fork_version_id": None,
        "created": 1620000000000,
        "updated": 1620000000000,
    }


@pytest.fixture(scope="function")
def parent_data():
    """Parent data."""
    return {
        "id": "9493793c-47d2-48e2-9867-ca597b4ebb41",
        "json": {
            "id": "1217214",
            "pid": {"pk": 2, "pid_type": "recid", "status": "R", "obj_type": "rec"},
            "access": {"owned_by": [{"user": 1234}]},
            "communities": {"ids": ["zenodo", "migration"], "default": "zenodo"},
        },
        "version_id": 1,
        "created": 1620000000000,
        "updated": 1620000000000,
    }


@pytest.fixture(scope="function")
def bucket_data():
    """Bucket data."""
    return {
        "id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "created": 1640995200000000,
        "updated": 1640995200000000,
        "default_location": 1,
        "default_storage_class": "L",
        "size": 0,
        "quota_size": 50000000000,
        "max_file_size": 50000000000,
        "locked": False,
        "deleted": False,
    }


@pytest.fixture(scope="function")
def pid_data():
    """PID data."""
    return {
        "id": 12132090,
        "pid_type": "recid",
        "pid_value": "1217215",
        "pid_provider": None,
        "status": "K",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "created": 1640995200000000,
        "updated": 1640995200000000,
    }


def test_create_draft_new(state, draft_data, parent_data, bucket_data, pid_data):
    data = dict(
        tx_id=1,
        pid=pid_data,
        bucket=bucket_data,
        draft=draft_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 7
    assert rows[0].type == OperationType.INSERT
    assert isinstance(rows[0].obj, PersistentIdentifier)
    assert rows[1].type == OperationType.INSERT
    assert isinstance(rows[1].obj, FilesBucket)
    assert rows[2].type == OperationType.INSERT
    assert isinstance(rows[2].obj, PersistentIdentifier)
    assert rows[3].type == OperationType.INSERT
    assert isinstance(rows[3].obj, RDMParentMetadata)
    assert rows[4].type == OperationType.UPDATE
    assert isinstance(rows[4].obj, PersistentIdentifier)
    assert rows[5].type == OperationType.INSERT
    assert isinstance(rows[5].obj, RDMDraftMetadata)
    assert rows[6].type == OperationType.INSERT
    assert isinstance(rows[6].obj, RDMVersionState)


def test_create_draft_new_version(
    state, draft_data, parent_data, bucket_data, pid_data
):
    # set existing parent so the action goes on the new version path
    state.PARENTS.add(
        parent_data["json"]["id"],  # recid
        {
            "id": parent_data["id"],
            "latest_id": "93c09d1d-47d2-48e2-9867-ca597b4ebb41",
            "latest_index": 1,
        },
    )
    data = dict(
        tx_id=1,
        pid=pid_data,
        bucket=bucket_data,
        draft=draft_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)

    rows = list(action.prepare())
    assert len(rows) == 5
    assert rows[0].type == OperationType.INSERT
    assert isinstance(rows[0].obj, PersistentIdentifier)
    assert rows[1].type == OperationType.INSERT
    assert isinstance(rows[1].obj, FilesBucket)
    assert rows[2].type == OperationType.UPDATE
    assert isinstance(rows[2].obj, PersistentIdentifier)
    assert rows[3].type == OperationType.INSERT
    assert isinstance(rows[3].obj, RDMDraftMetadata)
    assert rows[4].type == OperationType.INSERT
    assert isinstance(rows[4].obj, RDMVersionState)


def test_create_draft_published_draft(
    state, draft_data, parent_data, bucket_data, pid_data
):
    # set existing parent so the action goes on the new version path
    state.PARENTS.add(
        parent_data["json"]["id"],  # recid
        {
            "id": parent_data["id"],
            "latest_id": "93c09d1d-47d2-48e2-9867-ca597b4ebb41",
            "latest_index": 1,
        },
    )

    state.RECORDS.add(
        draft_data["json"]["id"],  # recid
        {
            "index": 1,
            "id": draft_data["id"],  # uuid
            "parent_id": parent_data["id"],  # parent uuid
            "fork_version_id": 1,
            "pids": {},
        },
    )
    data = dict(
        tx_id=1,
        pid=pid_data,
        bucket=bucket_data,
        draft=draft_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 4
    assert rows[0].type == OperationType.INSERT
    assert isinstance(rows[0].obj, PersistentIdentifier)
    assert rows[1].type == OperationType.INSERT
    assert isinstance(rows[1].obj, FilesBucket)
    assert rows[2].type == OperationType.INSERT
    assert isinstance(rows[2].obj, RDMDraftMetadata)
    assert rows[3].type == OperationType.UPDATE
    assert isinstance(rows[3].obj, RDMVersionState)
