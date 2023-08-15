# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Draft actions tests."""

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import DraftCreateAction, DraftEditAction
from invenio_rdm_migrator.streams.models.files import FilesBucket
from invenio_rdm_migrator.streams.models.pids import PersistentIdentifier
from invenio_rdm_migrator.streams.models.records import (
    RDMDraftMetadata,
    RDMParentMetadata,
    RDMVersionState,
)


def test_create_draft_new(
    state, draft_data, parent_data, bucket_data, draft_pid_data, parent_pid_data
):
    data = dict(
        tx_id=1,
        draft_pid=draft_pid_data,
        draft_bucket=bucket_data,
        draft=draft_data,
        parent_pid=parent_pid_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 7
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == PersistentIdentifier
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == FilesBucket
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == PersistentIdentifier
    assert rows[3].type == OperationType.INSERT
    assert rows[3].model == RDMParentMetadata
    assert rows[4].type == OperationType.UPDATE
    assert rows[4].model == PersistentIdentifier
    assert rows[5].type == OperationType.INSERT
    assert rows[5].model == RDMDraftMetadata
    assert rows[6].type == OperationType.INSERT
    assert rows[6].model == RDMVersionState


def test_create_draft_new_version(
    state, draft_data, parent_data, bucket_data, draft_pid_data, parent_pid_data
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
        draft_pid=draft_pid_data,
        draft_bucket=bucket_data,
        draft=draft_data,
        parent_pid=parent_pid_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)

    rows = list(action.prepare())
    assert len(rows) == 5
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == PersistentIdentifier
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == FilesBucket
    assert rows[2].type == OperationType.UPDATE
    assert rows[2].model == PersistentIdentifier
    assert rows[3].type == OperationType.INSERT
    assert rows[3].model == RDMDraftMetadata
    assert rows[4].type == OperationType.INSERT
    assert rows[4].model == RDMVersionState


def test_create_draft_published_of_record(
    state, draft_data, parent_data, bucket_data, draft_pid_data, parent_pid_data
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
        draft_pid=draft_pid_data,
        draft_bucket=bucket_data,
        draft=draft_data,
        parent_pid=parent_pid_data,
        parent=parent_data,
    )
    action = DraftCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 4
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == PersistentIdentifier
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == FilesBucket
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == RDMDraftMetadata
    assert rows[3].type == OperationType.UPDATE
    assert rows[3].model == RDMVersionState


def test_edit_draft(state, draft_data, parent_data):
    # draft id must be on the cache, set there by the draft create action
    parent_state = {
        "id": parent_data["id"],
        "next_draft_id": draft_data["id"],
    }
    state.PARENTS.add(parent_data["json"]["id"], parent_state)
    # the transform will bring in and empty id for both parent and draft
    del draft_data["id"]
    del parent_data["id"]

    data = dict(
        tx_id=1,
        draft=draft_data,
        parent=parent_data,
    )
    action = DraftEditAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == RDMParentMetadata
    assert rows[0].data == {"id": parent_state["id"], **parent_data}
    assert rows[1].type == OperationType.UPDATE
    assert rows[1].model == RDMDraftMetadata
    assert rows[1].data == {"id": parent_state["next_draft_id"], **draft_data}


def test_partial_edit_draft(state, draft_data, parent_data):
    # draft id must be on the cache, set there by the draft create action
    parent_state = {
        "id": parent_data["id"],
        "next_draft_id": draft_data["id"],
    }
    state.PARENTS.add(parent_data["json"]["id"], parent_state)
    # the transform will bring in and empty id for both parent and draft
    del draft_data["id"]
    del parent_data["id"]

    # remove some content to simulate partial updates
    for key in ["bucket_id", "parent_id", "expires_at", "created", "fork_version_id"]:
        del draft_data[key]

    for key in ["created", "version_id"]:
        del parent_data[key]

    data = dict(
        tx_id=1,
        draft=draft_data,
        parent=parent_data,
    )
    action = DraftEditAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == RDMParentMetadata
    assert set(rows[0].data.keys()) == {"id", "json", "updated"}
    assert rows[1].type == OperationType.UPDATE
    assert rows[1].model == RDMDraftMetadata
    assert set(rows[1].data.keys()) == {"id", "json", "version_id", "index", "updated"}
