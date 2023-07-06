# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities table generator tests."""


from invenio_rdm_migrator.streams.communities.load import CommunityTableGenerator
from invenio_rdm_migrator.streams.models.communities import (
    Community,
    CommunityFile,
    CommunityMember,
)
from invenio_rdm_migrator.streams.models.files import FilesBucket, FilesObjectVersion


def test_generate_rows(communities_state, transformed_community_entry_pks):
    """Test the row generation of the request table generator."""
    tg = CommunityTableGenerator(communities_state)
    rows = list(tg._generate_rows(transformed_community_entry_pks))
    expected_rows = [
        FilesBucket(
            id=1,
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            default_location=None,
            default_storage_class="L",
            size=0,
            quota_size=0,
            max_file_size=0,
            locked=False,
            deleted=False,
        ),
        Community(
            id="7357c033-abcd-1a2b-3c4d-123abc456def",
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            json={
                "title": "Migrator community",
                "description": "Migrator testing community",
                "page": "",
                "curation_policy": "",
            },
            version_id=1,
            slug="migrator",
            bucket_id=1,
        ),
        CommunityMember(
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            json={},
            version_id=1,
            role="owner",
            visible=True,
            active=True,
            community_id="7357c033-abcd-1a2b-3c4d-123abc456def",
            user_id=1,
            group_id=None,
            request_id=None,
        ),
        FilesObjectVersion(
            version_id=1,
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            key="logo",
            bucket_id=1,
            file_id="1",
            _mimetype=None,
            is_head=True,
        ),
        CommunityFile(
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            id="1",
            json={},
            version_id=1,
            key="logo",
            record_id="7357c033-abcd-1a2b-3c4d-123abc456def",
            object_version_id=1,
        ),
    ]

    assert rows == expected_rows
