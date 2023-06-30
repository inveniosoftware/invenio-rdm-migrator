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

from invenio_rdm_migrator.streams.files import FilesCopyLoad


@pytest.fixture(scope="function")
def files_copy_load(tmp_dir):
    """Request load instance."""
    # the db queries will be mocked
    load = FilesCopyLoad(db_uri="None", tmp_dir=tmp_dir.name)
    yield load
    load._cleanup()


@patch(
    "invenio_rdm_migrator.load.ids.uuid4",
    lambda: "12345678-abcd-1a2b-3c4d-123abc456def",
)
def test_files_load_prepare(files_copy_load, transformed_files_entry):
    """Test the table preparation (file creation)."""
    tables = [table for _, table in files_copy_load._prepare([transformed_files_entry])]

    # assert tables
    assert len(tables) == 3
    assert tables[0].__tablename__ == "files_files"
    assert tables[1].__tablename__ == "files_bucket"
    assert tables[2].__tablename__ == "files_object"

    # assert files were created and have the content
    files = list(os.scandir(files_copy_load.tmp_dir))
    assert len(files) == 3

    # assert files bucket content
    with open(f"{files_copy_load.tmp_dir}/files_bucket.csv", "r") as file:
        # id, created, updated, default_location, default_storage_class, size, quota_size, max_file_size,locked, deleted
        expected = (
            "1," "2023-04-19," "2023-04-19," "1," "L," "1234," "," "," "False," "False"
        )
        content = file.read().rstrip()
        assert content == expected
    # assert files object version content
    with open(f"{files_copy_load.tmp_dir}/files_files.csv", "r") as file:
        # id, created, updated, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check
        expected = (
            "3,"
            "2023-04-19,"
            "2023-04-19,"
            "path/to/file,"
            "L,"
            "1234,"
            "md5:abcd1234,"
            "True,"
            "True,"
            ","
            "False"
        )
        content = file.read().rstrip()
        assert content == expected
    # assert files instance content
    with open(f"{files_copy_load.tmp_dir}/files_object.csv", "r") as file:
        #  version_id, created, updated, key, bucket_id, file_id, _mimetype, is_head
        expected = "2," "2023-04-19," "2023-04-19," "file.txt," "1," "3," "," "True"
        content = file.read().rstrip()
        assert content == expected
