# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Null extract tests."""

from types import GeneratorType

import pytest

from invenio_rdm_migrator.extract.null import NullExtract


def test_run_method_does_not_raise_errors():
    extract = NullExtract()
    try:
        next(extract.run())
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_next_method_returns_none():
    extract = NullExtract()
    assert next(extract.run()) is None


def test_run_returns_iterator():
    extract = NullExtract()
    assert isinstance(extract.run(), GeneratorType)


def test_generator_object_only_returns_once():
    extract = NullExtract()
    gen = extract.run()
    next(gen)
    with pytest.raises(StopIteration):
        next(gen)
