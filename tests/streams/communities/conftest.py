# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Community stream fixtures."""

from copy import deepcopy

import pytest


@pytest.fixture(scope="module")
def transformed_community_entry():
    """Community data as after being transformed."""
    return {
        "community": {
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "slug": "migrator",
            "version_id": 1,
            "json": {
                "title": "Migrator community",
                "description": "Migrator testing community",
                "page": "",
                "curation_policy": "",
            },
            "bucket_id": "12345678-abcd-1a2b-3c4d-123abc456def",
        },
        "oai_set": {
            "created": "2023-01-01 12:00:00.00000",
            "updated": "2023-01-31 12:00:00.00000",
            "id": 1,
            "spec": "community-migrator",
            "name": "Migrator community",
            "description": "Migrator testing community",
        },
        "community_members": [
            {
                "created": "2023-01-01 12:00:00.00000",
                "updated": "2023-01-31 12:00:00.00000",
                "json": {},
                "version_id": 1,
                "role": "owner",
                "visible": True,
                "active": True,
                "user_id": 1,
                "group_id": None,
                "request_id": None,
            }
        ],
        "featured_community": {},
        "community_files": {
            "file": {
                "created": "2023-01-01 12:00:00.00000",
                "updated": "2023-01-31 12:00:00.00000",
                "id": "12345678-abcd-1a2b-3c4d-123abc456def",
                "json": {},
                "version_id": 1,
                "key": "logo",
            },
            "bucket": {
                "created": "2023-01-01 12:00:00.00000",
                "updated": "2023-01-31 12:00:00.00000",
                "default_location": None,
                "default_storage_class": "L",
                "size": 0,
                "quota_size": 0,
                "max_file_size": 0,
                "locked": False,
                "deleted": False,
                "id": "12345678-abcd-1a2b-3c4d-123abc456def",
            },
            "file_object": {
                "created": "2023-01-01 12:00:00.00000",
                "updated": "2023-01-31 12:00:00.00000",
                "bucket_id": "12345678-abcd-1a2b-3c4d-123abc456def",
                "version_id": "12345678-abcd-1a2b-3c4d-123abc456def",
                "key": "logo",
                "file_id": "12345678-abcd-1a2b-3c4d-123abc456def",
                "_mimetype": None,
                "is_head": True,
            },
        },
    }


@pytest.fixture(scope="module")
def transformed_community_entry_pks(transformed_community_entry):
    """Request data as after being transformed and passed by generate_pks.

    The last step would happen in the table_generator._prepare.
    """
    data = deepcopy(transformed_community_entry)
    data["community"]["id"] = "7357c033-abcd-1a2b-3c4d-123abc456def"
    data["community_members"][0]["id"] = "12345678-abcd-1a2b-3c4d-123abc456def"

    return data
