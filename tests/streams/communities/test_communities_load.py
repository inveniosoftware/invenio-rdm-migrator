# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities load tests."""

import os
from unittest.mock import patch

import pytest

from invenio_rdm_migrator.streams.communities import CommunityCopyLoad


@pytest.fixture(scope="function")
def community_copy_load(cache, tmp_dir):
    """Community load instance."""
    # the db queries will be mocked
    load = CommunityCopyLoad("None", tmp_dir.name, cache)
    yield load
    load._cleanup()


@patch(
    "invenio_rdm_migrator.load.ids.uuid4",
    lambda: "12345678-abcd-1a2b-3c4d-123abc456def",
)
def test_community_load_prepare(community_copy_load, transformed_community_entry):
    """Test the table preparation (file creation)."""
    tables = list(community_copy_load._prepare([transformed_community_entry]))

    # assert tables
    # it has four tables: communities, parent communities, communities_files and members
    expected_table_names = [
        "community_metadata",
        "communities_members",
        "rdm_parents_community",
        "communities_files",
        "files_object",
        "files_bucket",
    ]
    table_names = [table._table_name for table in tables]
    assert len(tables) == len(expected_table_names)
    assert any([e_table in table_names for e_table in expected_table_names])

    # assert files were created and have the content
    # five files are created: one for the communities, members, files, files bucket, files object
    files = list(os.scandir(community_copy_load.data_dir))
    assert len(files) == 5

    # assert communities metadata content
    with open(f"{community_copy_load.data_dir}/communities_metadata.csv", "r") as file:
        # uuid, json, created, updated, version_id, number, expired_at
        expected = (
            "12345678-abcd-1a2b-3c4d-123abc456def,"
            '2023-01-01 12:00:00.00000,2023-01-31 12:00:00.00000,"{""title"": ""Migrator community"", ""description"": ""Migrator testing community"", ""page"": """", ""curation_policy"": """"}",1,migrator,12345678-abcd-1a2b-3c4d-123abc456def\n'
        )
        content = file.read()
        assert content == expected

    # assert communities members content
    with open(f"{community_copy_load.data_dir}/communities_members.csv", "r") as file:
        # uuid, json, created, updated, version_id, number, expired_at
        expected = "12345678-abcd-1a2b-3c4d-123abc456def,2023-01-01 12:00:00.00000,2023-01-31 12:00:00.00000,{},1,owner,True,True,12345678-abcd-1a2b-3c4d-123abc456def,1,,\n"
        content = file.read()
        assert content == expected
