# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities table generator tests."""


from copy import deepcopy

import dictdiffer

from invenio_rdm_migrator.streams.communities.load import CommunityTableGenerator
from invenio_rdm_migrator.streams.communities.models import Community, CommunityMember


def test_generate_rows(transformed_community_entry_pks):
    """Test the row generation of the request table generator."""
    tg = CommunityTableGenerator({})  # no need for cache in this test
    rows = list(tg._generate_rows(transformed_community_entry_pks))
    expected_rows = [
        Community(
            id="12345678-abcd-1a2b-3c4d-123abc456def",
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
            community_id="12345678-abcd-1a2b-3c4d-123abc456def",
            user_id=1,
            group_id=None,
            request_id=None,
        ),
    ]

    assert rows == expected_rows
