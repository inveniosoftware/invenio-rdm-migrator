# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest requests configuration."""

from copy import deepcopy

import pytest


@pytest.fixture(scope="module")
def transformed_incl_req_entry():
    """Request data as after being transformed.

    `topic`, `receiver` and `created_by` could be different.
    This is a sample inclusion request for a record into a community.
    """
    return {
        "created": "01/01/2023",
        "updated": "01/01/2023",
        "version_id": "1",
        "json": {
            "type": "community-inclusion",
            "title": "title",
            "topic": {"record": "123456"},
            "status": "submitted",
            "receiver": {"community": "comm"},
            "created_by": {"user": "3"},
            "$schema": "local://requests/request-v1.0.0.json",
        },
        "number": "1",
        "expires_at": "01/01/2023",
    }


@pytest.fixture(scope="module")
def transformed_incl_req_entry_pks(transformed_incl_req_entry):
    """Request data as after being transformed and passed by generate_pks.

    The last step would happen in the table_generator._prepare.
    """
    data = deepcopy(transformed_incl_req_entry)
    data["id"] = "12345678-abcd-1a2b-3c4d-123abc456def"

    return data
