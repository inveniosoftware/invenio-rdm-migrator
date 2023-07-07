# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base transformation tests."""

from types import GeneratorType

import pytest

from invenio_rdm_migrator.logging import Logger
from invenio_rdm_migrator.transform import Transform
from invenio_rdm_migrator.transform.base import drop_nones

###
# Base class
###


def test_cannot_instantiate_base_class():
    with pytest.raises(TypeError):
        Transform()

    class Test(Transform):
        """Test Transform."""

        pass

    with pytest.raises(TypeError):
        Test()


class TestTransform(Transform):
    def _transform(self, entry):
        return entry * 2


def test_transform_returns_transformed_entry():
    t = TestTransform()
    assert list(t.run([1])) == [2]


def test_run_returns_iterator():
    extract = TestTransform()
    assert isinstance(extract.run([]), GeneratorType)


def test_run_continues_to_next_entry_when_exception_raised(capsys, tmp_path):
    Logger.initialize(tmp_path)

    class TestTransform(Transform):
        def _transform(self, entry):
            if entry == 2:
                raise Exception("Test exception")
            return entry

    t = TestTransform()
    # should raise and log exception on 2, log it and continue to 3
    assert list(t.run([1, 2, 3])) == [1, 3]
    captured = capsys.readouterr()
    assert "Test exception" in captured.err


###
# drop_nones
###


def test_simple_dict_no_nones():
    data = {"a": 1, "b": "hello", "c": [1, 2, 3]}
    assert drop_nones(data) == data


def test_nested_dict_no_nones():
    data = {"a": 1, "b": {"c": 2, "d": {"e": "hello"}}}
    assert drop_nones(data) == data


def test_empty_dict():
    data = {}
    assert drop_nones(data) == {}


def test_nested_dict_first_level_nones():
    data = {"a": 1, "b": {"c": None, "d": {"e": "hello", "f": None}}, "g": None}
    expected = {
        "a": 1,
        "b": {"d": {"e": "hello"}},
    }
    assert drop_nones(data) == expected


def test_nested_dict_some_nones():
    data = {"a": 1, "b": {"c": None, "d": {"e": "hello", "f": None}}, "g": None}
    expected = {
        "a": 1,
        "b": {"d": {"e": "hello"}},
    }
    assert drop_nones(data) == expected


def test_dict_only_nones():
    data = {"a": None, "b": None, "c": None}
    assert drop_nones(data) == {}
