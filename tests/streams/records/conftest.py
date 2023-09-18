# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest requests configuration."""

from copy import deepcopy

import pytest


@pytest.fixture(scope="function")
def transformed_record_entry():
    """Record entry after being transformed."""
    return {
        "parent": {
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "version_id": 1,
            "json": {
                "id": "12345677",
                "communities": {"ids": ["comm", "other-comm"], "default": "comm"},
            },
        },
        "record": {
            "id": "2d6970ea-602d-4e8b-a918-063a59823386",
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "version_id": 1,
            "index": 1,
            "bucket_id": "bur3c0rd-1234-abcd-1ab2-1234abcd56ef",
            "json": {
                "id": "12345678",
                "pids": {
                    "oai": {
                        "provider": "oai",
                        "identifier": "oai:zenodo.org:12345678",
                    },
                    "doi": {
                        "client": "datacite",
                        "provider": "datacite",
                        "identifier": "10.5281/zenodo.12345678",
                    },
                },
            },
        },
    }


@pytest.fixture(scope="function")
def transformed_record_entry_pks(transformed_record_entry):
    """Record data as after being transformed.

    It also includes generated PKs and resolved references.
    """
    data = deepcopy(transformed_record_entry)
    data["parent"]["id"] = "12345678-abcd-1a2b-3c4d-123abc456def"
    data["record"]["parent_id"] = "12345678-abcd-1a2b-3c4d-123abc456def"
    data["parent"]["json"]["pid"] = {
        "pk": 1_000_000,  # pk, not pid value
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "R",
    }
    data["parent"]["json"]["communities"] = {
        "ids": [
            "12345678-abcd-1a2b-3c4d-123abc456def",
            "12345678-abcd-1a2b-3c4d-123abc123abc",
        ],
        "default": "12345678-abcd-1a2b-3c4d-123abc456def",
    }
    data["record"]["json"]["pid"] = {
        "pk": 1_000_001,  # pk, not pid value
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "R",
    }

    return data


@pytest.fixture(scope="function")
def transformed_draft_entry():
    """Draft entry after being transformed."""
    return {
        "parent": {
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "version_id": 1,
            "json": {
                "id": "12345677",
                "communities": {"ids": ["comm", "other-comm"], "default": "comm"},
            },
        },
        "draft": {
            "id": "2d6970ea-602d-4e8b-a918-063a59823386",
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "version_id": 1,
            "index": 1,
            "bucket_id": "b0c73700-1234-abcd-1ab2-1234abcd56ef",
            "json": {
                "id": "12345678",
                "pids": {
                    "doi": {
                        "provider": "external",
                        "identifier": "10.1234/foo",
                    },
                },
            },
            "expires_at": "2024-01-01 12:00:00.00000",
            "fork_version_id": None,
        },
    }


@pytest.fixture(scope="function")
def transformed_draft_entry_pks(transformed_draft_entry):
    """Draft data as after being transformed.

    It also includes generated PKs and resolved references.
    """
    data = deepcopy(transformed_draft_entry)
    data["parent"]["id"] = "12345678-abcd-1a2b-3c4d-123abc456def"
    data["draft"]["parent_id"] = "12345678-abcd-1a2b-3c4d-123abc456def"
    data["parent"]["json"]["pid"] = {
        "pk": 1_000_000,
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "N",
    }
    data["parent"]["json"]["communities"] = {
        "ids": [
            "12345678-abcd-1a2b-3c4d-123abc456def",
            "12345678-abcd-1a2b-3c4d-123abc123abc",
        ],
        "default": "12345678-abcd-1a2b-3c4d-123abc456def",
    }
    data["draft"]["json"]["pid"] = {
        "pk": 1_000_001,
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "N",
    }
    return data
