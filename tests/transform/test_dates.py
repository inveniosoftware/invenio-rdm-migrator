# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Datetime transformation tests."""

from datetime import datetime

from invenio_rdm_migrator.transform import DatetimeMixin


class TestTransform(DatetimeMixin):
    """Test Datetime transform."""

    pass


def test_date_microseconds():
    data = {"one": 1620000000000000, "two": 1620000000000000, "three": 1620000000000000}

    TestTransform()._microseconds_to_isodate(data=data, fields=["one", "two"])

    assert data == {
        "one": "2021-05-03T00:00:00",
        "two": "2021-05-03T00:00:00",
        "three": 1620000000000000,  # left untouched
    }


def test_date_microseconds_no_int():
    data = {"one": "1620000000000000"}

    TestTransform()._microseconds_to_isodate(data=data, fields=["one"])

    assert data == {"one": "1620000000000000"}


def test_date_milliseconds():
    data = {"one": 1620000000000, "two": 1620000000000, "three": 1620000000000}

    TestTransform()._milliseconds_to_isodate(data=data, fields=["one", "two"])

    assert data == {
        "one": "2021-05-03T00:00:00",
        "two": "2021-05-03T00:00:00",
        "three": 1620000000000,  # left untouched
    }


def test_date_milliseconds_no_int():
    data = {"one": "1620000000000"}

    TestTransform()._milliseconds_to_isodate(data=data, fields=["one"])

    assert data == {"one": "1620000000000"}
