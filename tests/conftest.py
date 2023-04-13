# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import tempfile

import pytest

from invenio_rdm_migrator.streams.cache import ParentCache


@pytest.fixture(scope="function")
def tmp_dir():
    """Yields a temporary directory."""
    tmp_dir = tempfile.TemporaryDirectory()
    yield tmp_dir
    tmp_dir.cleanup()


@pytest.fixture(scope="module")
def parent_cache():
    """Records parent cache.

    Keys are concept recids and values are UUIDs.
    """
    cache = ParentCache()
    cache.add(
        "123456",
        {
            "id": "1234abcd-1234-5678-abcd-123abc456def",
            "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "latest_index": 1,
        },
    )
    return cache


@pytest.fixture(scope="module")
def communities_cache():
    """Communities cache.

    Keys are community slugs and values are UUIDs.
    """
    return {"comm": "12345678-abcd-1a2b-3c4d-123abc456def"}


@pytest.fixture(scope="module")
def cache(parent_cache, communities_cache):
    """Global cache containing the other ones."""
    return {
        "parents": parent_cache,
        "communities": communities_cache,
    }
