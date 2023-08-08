# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils tests."""

import json
import re
from uuid import UUID

import pytest

from invenio_rdm_migrator.utils import JSONEncoder, dict_set, ts

###
# timestamp
###


def test_current_timestamp_iso():
    assert isinstance(ts(), str)


def test_current_timestamp():
    assert isinstance(ts(iso=False), float)


def test_current_timestamp_fmt():
    value = ts(fmt="%Y-%m-%dT%H:%M:%S")
    exp = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    assert exp.match(value)


###
# JSONEncoder
###


def test_no_uuid_values():
    data = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}
    encoded_data = JSONEncoder().encode(data)
    assert encoded_data == json.dumps(data)


def test_unknown_values():
    class Unknown:
        """Needed to trigger the encoder type error."""

        pass

    data = {"key": Unknown()}
    pytest.raises(TypeError, JSONEncoder().encode, data)


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


###
# Dict set
###


def test_existing_root():
    source = {"a": {"b": 1}}
    key = "a.c"
    value = 2
    dict_set(source, key, value)
    assert source == {"a": {"b": 1, "c": 2}}


def test_set_existing_key():
    source = {"a": {"b": 1}}
    key = "a.b"
    value = 2
    dict_set(source, key, value)
    assert source == {"a": {"b": 2}}


def test_set_list():
    source = {"a": {}}
    key = "a.b"
    value = [1, 2]
    dict_set(source, key, value)
    assert source == {"a": {"b": [1, 2]}}


def test_set_empty_root():
    source = {}
    key = "a.b"
    value = 6
    dict_set(source, key, value)
    assert source == {"a": {"b": 6}}


def test_set_empty_root_list_key():
    source = {}
    key = ["a", "b"]
    value = 6
    dict_set(source, key, value)
    assert source == {"a": {"b": 6}}


def test_nested_dict():
    source = {"a": {"b": {}}}
    key = "a.b.c.d"
    value = 3
    dict_set(source, key, value)
    assert source == {"a": {"b": {"c": {"d": 3}}}}


def test_int_key():
    source = {1: ""}
    key = 1
    value = 3
    # "lookup must be string or list"
    pytest.raises(TypeError, dict_set, source, key, value)


def test_no_key():
    source = {"a": "value"}
    key = None
    value = 3
    # ("No lookup key specified"
    pytest.raises(KeyError, dict_set, source, key, value)
