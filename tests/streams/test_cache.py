# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cache tests."""

import pytest

from invenio_rdm_migrator.streams.cache import Cache, ParentsCache, RecordsCache


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
