# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest files configuration."""


import pytest


@pytest.fixture(scope="module")
def transformed_files_entry():
    """Files data as after being transformed.

    These are sample files related information.
    """
    return {
        "bucket": {
            "id": "1",
            "created": "2023-04-19",
            "updated": "2023-04-19",
            "default_location": "1",
            "default_storage_class": "L",
            "size": 1234,
            "quota_size": None,
            "max_file_size": None,
            "locked": False,
            "deleted": False,
        },
        "object_version": {
            "version_id": "2",
            "created": "2023-04-19",
            "updated": "2023-04-19",
            "key": "file.txt",
            "bucket_id": "1",
            "file_id": "3",
            "_mimetype": None,
            "is_head": True,
        },
        "file": {
            "id": "3",
            "created": "2023-04-19",
            "updated": "2023-04-19",
            "uri": "path/to/file",
            "storage_class": "L",
            "size": 1234,
            "checksum": "md5:abcd1234",
            "readable": True,
            "writable": True,
            "last_check_at": None,
            "last_check": False,
        },
    }
