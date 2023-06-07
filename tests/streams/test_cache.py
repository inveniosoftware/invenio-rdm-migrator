# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""State tests."""

import json
from pathlib import Path

import pytest

from invenio_rdm_migrator.load.ids import pid_pk
from invenio_rdm_migrator.state import (
    CommunitiesState,
    ParentsState,
    PIDMaxPKState,
    RecordsState,
)
from invenio_rdm_migrator.state.base import State

###
# Parent State
###


@pytest.fixture(scope="function")
def parents_state():
    """Parents state."""
    return ParentsState()


def test_parent_state_record_entry(parents_state):
    parents_state.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert parents_state.get("123")
    assert parents_state.get(123)  # test num to string conversion


def test_parent_state_draft_entry(parents_state):
    parents_state.add(
        "123",
        {
            "id": "parent-uuid",
            "next_draft_id": "draft-uuid",
        },
    )
    assert parents_state.get("123")
    assert parents_state.get(123)  # test num to string conversion


def test_parent_state_update_record(parents_state):
    parents_state.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert not parents_state.get("123").get("next_draft_id")

    parents_state.update(
        "123",
        {
            "latest_index": 100,
            "latest_id": "new-record-uuid",
        },
    )
    assert parents_state.get("123").get("latest_index") == 100
    assert parents_state.get("123").get("latest_id") == "new-record-uuid"


def test_parent_state_update_draft(parents_state):
    parents_state.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert not parents_state.get("123").get("next_draft_id")

    parents_state.update(
        "123",
        {
            "next_draft_id": "draft-uuid",
        },
    )
    assert parents_state.get("123").get("next_draft_id") == "draft-uuid"


def test_parent_state_invalid_entries(parents_state):
    invalid = [
        {  # no id
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
        {  # missing lastest index
            "id": "parent-uuid",
            "latest_id": "record-uuid",
        },
        {  # no latest id nor next draft id
            "id": "parent-uuid",
            "latest_index": 1,
        },
    ]

    for entry in invalid:
        pytest.raises(AssertionError, parents_state.add, "123", entry)


###
# Record State
###


@pytest.fixture(scope="function")
def records_state():
    """Records state."""
    return RecordsState()


def test_record_state_record_entry(records_state):
    records_state.add(
        "123",
        {
            "index": 1,
            "id": "record-uuid",
            "parent_id": "parent-uuid",
            "fork_version_id": 1,
        },
    )
    assert records_state.get("123")
    assert records_state.get(123)  # test num to string conversion


def test_record_state_invalid_entries(records_state):
    invalid = [
        {
            "id": "record-uuid",
            "parent_id": "parent-uuid",
            "fork_version_id": 1,
        },
        {
            "index": 1,
            "parent_id": "parent-uuid",
            "fork_version_id": 1,
        },
        {
            "index": 1,
            "id": "record-uuid",
            "fork_version_id": 1,
        },
        {
            "index": 1,
            "id": "record-uuid",
            "parent_id": "parent-uuid",
        },
    ]

    for entry in invalid:
        pytest.raises(AssertionError, records_state.add, "123", entry)


###
# State
###


class MockState(State):
    """Mock State."""

    def _validate(self, data):
        """Validate data value is not 2."""
        assert not data["value"] == 2


@pytest.fixture(scope="function")
def data_file(tmp_dir):
    """State data filepath."""
    filepath = Path(tmp_dir.name) / "data.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"one": {"value": 1}, "two": {"value": 2}}))

    return filepath


def test_state_from_source_data_no_validation(data_file):
    """Test creating a state with initial data."""
    state = MockState(data_file)

    assert state.get("one")
    assert state.get("two")
    assert len(state.all()) == 2


def test_state_from_source_data_with_validation(data_file):
    """Test creating a state with initial data."""
    with pytest.raises(AssertionError):
        _ = MockState(data_file, validate=True)


def test_state_dump_data(tmp_dir):
    """Test dumping the data of the state."""
    state = MockState()

    state.add("one", {"value": 1})
    state.add("three", {"value": 3})
    state.add("four", {"value": 4})

    filepath = Path(tmp_dir.name) / "dump.json"
    state.dump(filepath)

    with open(filepath, "r") as file:
        expected = '{"one": {"value": 1}, "three": {"value": 3}, "four": {"value": 4}}'
        content = file.read()
        assert content == expected


###
# PIDMaxPK State
###


@pytest.fixture(scope="function")
def pid_max_pk():
    """Max PID PK state."""
    return PIDMaxPKState()


def test_pid_max_pk_state_add(pid_max_pk):
    pytest.raises(NotImplementedError, pid_max_pk.add, "key", "value")


def test_pid_max_pk_state_update(pid_max_pk):
    pytest.raises(NotImplementedError, pid_max_pk.update, "max_value", "value")


def test_pid_max_pk_state_dump(tmp_dir, pid_max_pk):
    filepath = Path(tmp_dir.name) / "dump.json"
    pid_pk()
    pid_max_pk.dump(filepath)

    with open(filepath, "r") as file:
        # f-string cannot have backslash needed for json dump
        expected = '{"max_value": 1000000}'
        content = file.read()
        assert content == expected


def test_pid_max_pk_state_load(tmp_dir):
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": 10}))

    state = PIDMaxPKState(filepath, validate=True)
    assert state.get("max_value") == 10


def test_pid_max_pk_state_validation_no_int(tmp_dir):
    # loading an int is tested implicitly in the previous test
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": "10"}))

    with pytest.raises(AssertionError):
        PIDMaxPKState(filepath, validate=True)


###
# Communities state
###


def test_communities_state_validation_no_uuid(tmp_dir):
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": "10"}))

    with pytest.raises(AssertionError):
        CommunitiesState(filepath, validate=True)


def test_communities_state_get():
    state = CommunitiesState()
    state.add("exists", "12345678-abcd-1a2b-3c4d-123abc456def")

    assert not state.get("other")
    assert state.get("exists") == "12345678-abcd-1a2b-3c4d-123abc456def"
