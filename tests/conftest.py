# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import tempfile

import pytest

from invenio_rdm_migrator.state import STATE, StateDB
from invenio_rdm_migrator.streams.records.state import ParentModelValidator

pytest_plugins = ("invenio_rdm_migrator.testutils",)


@pytest.fixture(scope="function")
def tmp_dir():
    """Yields a temporary directory."""
    tmp_dir = tempfile.TemporaryDirectory()
    yield tmp_dir
    tmp_dir.cleanup()


@pytest.fixture(scope="function")
def state(tmp_dir):
    """Yields a state.

    Do not call `save` on this fixture. The in memory database will be reset on each
    function, therefore no information will be persisted from test to test.
    """
    state_db = StateDB(
        db_dir=tmp_dir.name, validators={"parents": ParentModelValidator}
    )
    STATE.initialized_state(state_db, cache=False)

    return STATE


@pytest.fixture(scope="function")
def parents_state(state):
    """Records parent state.

    Keys are concept recids and values are dictionaries.
    """
    state.PARENTS.add(
        "123456",
        {
            "id": "1234abcd-1234-5678-abcd-123abc456def",
            "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "latest_index": 1,
        },
    )

    return state


@pytest.fixture(scope="function")
def communities_state(state):
    """Communities state."""
    state.COMMUNITIES.add(
        "comm",
        {
            "id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "bucket_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "oai_set_id": 1,
            "community_file_id": None,
            "logo_object_version_id": None,
        },
    )

    return state.COMMUNITIES


@pytest.fixture(scope="function")
def secret_keys_state(state):
    """Adds secret keys to global state."""
    state.VALUES.add(
        "old_secret_key",
        {"value": bytes("OLDKEY", "utf-8")},
    )
    state.VALUES.add(
        "new_secret_key",
        {"value": bytes("NEWKEY", "utf-8")},
    )
    return state


@pytest.fixture(scope="function")
def buckets_state(state):
    """Adds a bucket to draft map to the state."""
    state.BUCKETS.add(
        "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        {"draft_id": "d94f793c-47d2-48e2-9867-ca597b4ebb41"},
    )
    return state
