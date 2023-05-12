# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cache tests."""

import json
from pathlib import Path

import pytest

from invenio_rdm_migrator.load.ids import pid_pk
from invenio_rdm_migrator.streams.cache import (
    CommunitiesCache,
    ParentsCache,
    PIDMaxPKCache,
    RecordsCache,
)
from invenio_rdm_migrator.streams.cache.base import Cache

###
# Parent Cache
###


@pytest.fixture(scope="function")
def parents_cache():
    """Parents cache."""
    return ParentsCache()


def test_parent_cache_record_entry(parents_cache):
    parents_cache.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert parents_cache.get("123")
    assert parents_cache.get(123)  # test num to string conversion


def test_parent_cache_draft_entry(parents_cache):
    parents_cache.add(
        "123",
        {
            "id": "parent-uuid",
            "next_draft_id": "draft-uuid",
        },
    )
    assert parents_cache.get("123")
    assert parents_cache.get(123)  # test num to string conversion


def test_parent_cache_update_record(parents_cache):
    parents_cache.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert not parents_cache.get("123").get("next_draft_id")

    parents_cache.update(
        "123",
        {
            "latest_index": 100,
            "latest_id": "new-record-uuid",
        },
    )
    assert parents_cache.get("123").get("latest_index") == 100
    assert parents_cache.get("123").get("latest_id") == "new-record-uuid"


def test_parent_cache_update_draft(parents_cache):
    parents_cache.add(
        "123",
        {
            "id": "parent-uuid",
            "latest_index": 1,
            "latest_id": "record-uuid",
        },
    )
    assert not parents_cache.get("123").get("next_draft_id")

    parents_cache.update(
        "123",
        {
            "next_draft_id": "draft-uuid",
        },
    )
    assert parents_cache.get("123").get("next_draft_id") == "draft-uuid"


def test_parent_cache_invalid_entries(parents_cache):
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
        pytest.raises(AssertionError, parents_cache.add, "123", entry)


###
# Record Cache
###


@pytest.fixture(scope="function")
def records_cache():
    """Records cache."""
    return RecordsCache()


def test_record_cache_record_entry(records_cache):
    records_cache.add(
        "123",
        {
            "index": 1,
            "id": "record-uuid",
            "parent_id": "parent-uuid",
            "fork_version_id": 1,
        },
    )
    assert records_cache.get("123")
    assert records_cache.get(123)  # test num to string conversion


def test_record_cache_invalid_entries(records_cache):
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
        pytest.raises(AssertionError, records_cache.add, "123", entry)


###
# Cache
###


class MockCache(Cache):
    """Mock Cache."""

    def _validate(self, data):
        """Validate data value is not 2."""
        assert not data["value"] == 2


@pytest.fixture(scope="function")
def data_file(tmp_dir):
    """Cache data filepath."""
    filepath = Path(tmp_dir.name) / "data.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"one": {"value": 1}, "two": {"value": 2}}))

    return filepath


def test_cache_from_source_data_no_validation(data_file):
    """Test creating a cache with initial data."""
    cache = MockCache(data_file)

    assert cache.get("one")
    assert cache.get("two")
    assert len(cache.all()) == 2


def test_cache_from_source_data_with_validation(data_file):
    """Test creating a cache with initial data."""
    with pytest.raises(AssertionError):
        _ = MockCache(data_file, validate=True)


def test_cache_dump_data(tmp_dir):
    """Test dumping the data of the cache."""
    cache = MockCache()

    cache.add("one", {"value": 1})
    cache.add("three", {"value": 3})
    cache.add("four", {"value": 4})

    filepath = Path(tmp_dir.name) / "dump.json"
    cache.dump(filepath)

    with open(filepath, "r") as file:
        expected = '{"one": {"value": 1}, "three": {"value": 3}, "four": {"value": 4}}'
        content = file.read()
        assert content == expected


###
# PIDMaxPK Cache
###


@pytest.fixture(scope="function")
def pid_max_pk():
    """Max PID PK cache."""
    return PIDMaxPKCache()


def test_pid_max_pk_cache_add(pid_max_pk):
    pytest.raises(NotImplementedError, pid_max_pk.add, "key", "value")


def test_pid_max_pk_cache_update(pid_max_pk):
    pytest.raises(NotImplementedError, pid_max_pk.update, "max_value", "value")


def test_pid_max_pk_cache_dump(tmp_dir, pid_max_pk):
    filepath = Path(tmp_dir.name) / "dump.json"
    pid_pk()
    pid_max_pk.dump(filepath)

    with open(filepath, "r") as file:
        # f-string cannot have backslash needed for json dump
        expected = '{"max_value": 1000000}'
        content = file.read()
        assert content == expected


def test_pid_max_pk_cache_load(tmp_dir):
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": 10}))

    cache = PIDMaxPKCache(filepath, validate=True)
    assert cache.get("max_value") == 10


def test_pid_max_pk_cache_validation_no_int(tmp_dir):
    # loading an int is tested implicitly in the previous test
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": "10"}))

    with pytest.raises(AssertionError):
        PIDMaxPKCache(filepath, validate=True)


###
# Communities cache
###


def test_communities_cache_validation_no_uuid(tmp_dir):
    filepath = Path(tmp_dir.name) / "dump.json"
    with open(filepath, "w") as file:
        file.write(json.dumps({"max_value": "10"}))

    with pytest.raises(AssertionError):
        CommunitiesCache(filepath, validate=True)


def test_communities_cache_get():
    cache = CommunitiesCache()
    cache.add("exists", "12345678-abcd-1a2b-3c4d-123abc456def")

    assert not cache.get("other")
    assert cache.get("exists") == "12345678-abcd-1a2b-3c4d-123abc456def"
