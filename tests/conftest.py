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
    STATE.initialized_state(state_db)

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
    """Communities state.

    Keys are community slugs and values are UUIDs.
    """
    state.COMMUNITIES.add("comm", {"id": "12345678-abcd-1a2b-3c4d-123abc456def"})

    return state
