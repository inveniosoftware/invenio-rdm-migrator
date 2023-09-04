# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Requests load tests."""

import os
from unittest.mock import patch

import pytest

from invenio_rdm_migrator.streams.requests import RequestCopyLoad


@pytest.fixture(scope="function")
def request_copy_load(communities_state, tmp_dir):
    """Request load instance."""
    # the db queries will be mocked
    load = RequestCopyLoad(db_uri="None", tmp_dir=tmp_dir.name)
    yield load
    load._cleanup()


@patch(
    "invenio_rdm_migrator.load.ids.uuid4",
    lambda: "12345678-abcd-1a2b-3c4d-123abc456def",
)
def test_request_load_prepare(request_copy_load, transformed_incl_req_entry):
    """Test the table preparation (file creation)."""
    tables = [
        table for _, table in request_copy_load._prepare([transformed_incl_req_entry])
    ]

    # assert tables
    assert len(tables) == 1
    assert tables[0].__tablename__ == "request_metadata"

    # assert files were created and have the content
    files = list(os.scandir(request_copy_load.tmp_dir))
    assert len(files) == 1

    # assert request metadata content
    with open(f"{request_copy_load.tmp_dir}/request_metadata.csv", "r") as file:
        # uuid, json, created, updated, version_id, number, expired_at
        expected = (
            "12345678-abcd-1a2b-3c4d-123abc456def,"
            '"{""type"":""community-inclusion"",""title"":""title"",""topic"":{""record"":""123456""},""status"":""submitted"",""receiver"":{""community"":""12345678-abcd-1a2b-3c4d-123abc456def""},""created_by"":{""user"":""3""},""$schema"":""local://requests/request-v1.0.0.json""}"'
            ",01/01/2023,01/01/2023,1,1,01/01/2023\n"
        )
        content = file.read()
        assert content == expected
