# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import FileUploadAction
from invenio_rdm_migrator.streams.models.files import (
    FilesBucket,
    FilesInstance,
    FilesObjectVersion,
)
from invenio_rdm_migrator.streams.models.records import RDMDraftFile


@pytest.fixture(scope="function")
def bucket_data():
    """Bucket data."""
    return {
        "id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "default_location": 1,
        "default_storage_class": "S",
        "size": 1562554,
        "quota_size": 50000000000,
        "max_file_size": 50000000000,
        "locked": False,
        "deleted": False,
    }


@pytest.fixture(scope="function")
def ov_data():
    """Object version data."""
    return {
        "version_id": "f8200dc7-55b6-4785-abd0-f3d13b143c98",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "key": "IMG_3535.jpg",
        "bucket_id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "file_id": "e94b243e-9c0c-44df-bd1f-6decc374cf78",
        "_mimetype": None,
        "is_head": True,
    }


@pytest.fixture(scope="function")
def fi_data():
    """File instance data."""
    return {
        "id": "e94b243e-9c0c-44df-bd1f-6decc374cf78",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "uri": "root://eosmedia.cern.ch//eos/media/zenodo/test/data/e9/4b/243e-9c0c-44df-bd1f-6decc374cf78/data",
        "storage_class": "S",
        "size": 1562554,
        "checksum": "md5:3cc016be06f2be46d3a438db23c40bf3",
        "readable": True,
        "writable": False,
        "last_check_at": None,
        "last_check": True,
    }


@pytest.fixture(scope="function")
def fr_data(ov_data):
    """File record data."""
    return {
        "id": None,
        "json": {},
        "created": ov_data["created"],
        "updated": ov_data["updated"],
        "version_id": 1,
        "key": ov_data["key"],
        "record_id": None,
        "object_version_id": ov_data["version_id"],
    }


# TODO: add to state the bucket
def test_upload_file_action(buckets_state, bucket_data, fi_data, ov_data, fr_data):
    data = dict(
        tx_id=1,
        bucket=bucket_data,
        object_version=ov_data,
        file_instance=fi_data,
        file_record=fr_data,
    )
    action = FileUploadAction(data)
    rows = list(action.prepare())

    assert len(rows) == 4
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == FilesBucket
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == FilesObjectVersion
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == FilesInstance
    assert rows[3].type == OperationType.INSERT
    assert rows[3].model == RDMDraftFile
    assert rows[3].data["id"] is not None
    assert rows[3].data["record_id"] is not None
