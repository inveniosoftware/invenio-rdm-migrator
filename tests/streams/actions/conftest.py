# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Action streams test configuration."""

import pytest


###
# Draft
###
@pytest.fixture(scope="function")
def draft_pid_data():
    """PID data."""
    return {
        "id": 12132090,
        "pid_type": "recid",
        "pid_value": "1217215",
        "pid_provider": None,
        "status": "K",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
    }


@pytest.fixture(scope="function")
def draft_doi_data():
    """PID data."""
    return {
        "id": 12132092,
        "pid_type": "doi",
        "pid_value": "10.12345/rdm.1217215",
        "pid_provider": None,
        "status": "K",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
    }


@pytest.fixture(scope="function")
def draft_data():
    """Draft data."""
    return {
        "id": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "json": {
            "id": "1217215",
            "$schema": "https://zenodo.org/schemas/deposits/records/record-v1.0.0.json",
            "pids": {},
            "files": {"enabled": True},
            "metadata": {},
            "access": {
                "record": "public",
                "files": "public",
            },
            "custom_fields": {},
        },
        "version_id": 1,
        "index": 1,
        "bucket_id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "parent_id": "9493793c-47d2-48e2-9867-ca597b4ebb42",
        "expires_at": None,
        "fork_version_id": None,
        "created": "2021-05-01T00:00:00",
        "updated": "2021-05-01T00:00:00",
    }


###
# Parent
###


@pytest.fixture(scope="function")
def parent_pid_data():
    """PID data."""
    return {
        "id": 12132091,
        "pid_type": "recid",
        "pid_value": "1217214",
        "pid_provider": None,
        "status": "R",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb42",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
    }


@pytest.fixture(scope="function")
def parent_doi_data():
    """PID data."""
    return {
        "id": 12132093,
        "pid_type": "doi",
        "pid_value": "10.12345/rdm.1217214",
        "pid_provider": None,
        "status": "K",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
    }


@pytest.fixture(scope="function")
def parent_data():
    """Parent data."""
    return {
        "id": "9493793c-47d2-48e2-9867-ca597b4ebb42",
        "json": {
            "id": "1217214",
            "pid": {"pk": 2, "pid_type": "recid", "status": "R", "obj_type": "rec"},
            "access": {"owned_by": {"user": 1234}},
            "communities": {"ids": ["zenodo", "migration"], "default": "zenodo"},
        },
        "version_id": 1,
        "created": "2021-05-01T00:00:00",
        "updated": "2021-05-01T00:00:00",
    }


###
# Record
###


@pytest.fixture(scope="function")
def record_oai_data():
    """PID data."""
    return {
        "id": 12132094,
        "pid_type": "oai",
        "pid_value": "oai:zenodo.org:1217215",
        "pid_provider": None,
        "status": "K",
        "object_type": "rec",
        "object_uuid": "d94f793c-47d2-48e2-9867-ca597b4ebb41",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
    }


###
# Files
###


@pytest.fixture(scope="function")
def bucket_data():
    """Bucket data."""
    return {
        "id": "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
        "default_location": 1,
        "default_storage_class": "L",
        "size": 0,
        "quota_size": 50000000000,
        "max_file_size": 50000000000,
        "locked": False,
        "deleted": False,
    }


@pytest.fixture(scope="function")
def bucket_data_w_size():
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
