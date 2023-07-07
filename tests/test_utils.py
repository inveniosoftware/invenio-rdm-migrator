# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils tests."""

import json
from uuid import UUID

from invenio_rdm_migrator.utils import JSONEncoder, ts

###
# timestamp
###


def test_current_timestamp_iso():
    assert isinstance(ts(), str)


def test_current_timestamp():
    assert isinstance(ts(iso=False), float)


###
# JSONEncoder
###


def test_no_uuid_values():
    data = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}
    encoded_data = JSONEncoder().encode(data)
    assert encoded_data == json.dumps(data)


def test_uuid_values():
    data = {
        "key1": UUID("123e4567-e89b-12d3-a456-426655440000"),
    }
    expected_data = {
        "key1": "123e4567-e89b-12d3-a456-426655440000",
    }
    encoded_data = JSONEncoder().encode(data)
    assert encoded_data == json.dumps(expected_data)


def test_nested_uuid_values():
    data = {
        "key1": {"key2": UUID("123e4567-e89b-12d3-a456-426655440000")},
    }
    expected_data = {
        "key1": {"key2": "123e4567-e89b-12d3-a456-426655440000"},
    }
    encoded_data = JSONEncoder().encode(data)
    assert encoded_data == json.dumps(expected_data)
