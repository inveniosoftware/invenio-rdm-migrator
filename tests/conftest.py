# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import tempfile

import pytest

from invenio_rdm_migrator.state import CommunitiesState, ParentsState, RecordsState


@pytest.fixture(scope="function")
def tmp_dir():
    """Yields a temporary directory."""
    tmp_dir = tempfile.TemporaryDirectory()
    yield tmp_dir
    tmp_dir.cleanup()


@pytest.fixture(scope="function")
def parents_state():
    """Records parent state.

    Keys are concept recids and values are dictionaries.
    """
    state = ParentsState()
    state.add(
        "123456",
        {
            "id": "1234abcd-1234-5678-abcd-123abc456def",
            "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "latest_index": 1,
        },
    )
    return state


@pytest.fixture(scope="function")
def records_state():
    """Records state.

    Keys are recids and values are dictionaries.
    """
    state = RecordsState()
    return state


@pytest.fixture(scope="function")
def communities_state():
    """Communities state.

    Keys are community slugs and values are UUIDs.
    """
    state = CommunitiesState()
    state.add("comm", "12345678-abcd-1a2b-3c4d-123abc456def")
    state.add("other-comm", "12345678-abcd-1a2b-3c4d-123abc123abc")

    return state


@pytest.fixture(scope="function")
def state(parents_state, records_state, communities_state):
    """Global state containing the other ones."""
    return {
        "parents": parents_state,
        "records": records_state,
        "communities": communities_state,
    }
