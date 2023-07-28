# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Requests table generator tests."""

from copy import deepcopy

import dictdiffer

from invenio_rdm_migrator.streams.models.requests import RequestMetadata
from invenio_rdm_migrator.streams.requests.load import RequestTableGenerator


def test_generate_rows(communities_state, transformed_incl_req_entry_pks):
    """Test the row generation of the request table generator."""
    tg = RequestTableGenerator()  # no need for state in this test
    rows = list(tg._generate_rows(transformed_incl_req_entry_pks))
    expected_rows = [
        RequestMetadata(
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            json={
                "type": "community-inclusion",
                "title": "title",
                "topic": {"record": "123456"},
                "status": "submitted",
                "receiver": {"community": "comm"},
                "created_by": {"user": "3"},
                "$schema": "local://requests/request-v1.0.0.json",
            },
            created="01/01/2023",
            updated="01/01/2023",
            version_id="1",
            number="1",
            expires_at="01/01/2023",
        ),
    ]

    assert rows == expected_rows


def test_resolve_references(communities_state, transformed_incl_req_entry_pks):
    """Test the parent and community reference resolution."""
    expected = deepcopy(transformed_incl_req_entry_pks)
    expected["json"]["receiver"]["community"] = "12345678-abcd-1a2b-3c4d-123abc456def"

    tg = RequestTableGenerator()
    tg._resolve_references(transformed_incl_req_entry_pks)  # changes in place

    assert not list(dictdiffer.diff(transformed_incl_req_entry_pks, expected))
