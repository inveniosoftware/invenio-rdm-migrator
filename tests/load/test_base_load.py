# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base load tests."""

import pytest

from invenio_rdm_migrator.load import Load


def test_cannot_instantiate_base_class():
    with pytest.raises(TypeError):
        Load()

    class Test(Load):
        """Test Load."""

        pass

    with pytest.raises(TypeError):
        Test()


class BaseTestLoad(Load):
    """Test load implementation."""

    def _prepare(self, entry):
        pass

    def _load(self, entry):
        pass

    def _cleanup(self):
        pass


def test_entries_loaded_successfully():
    test_load_impl = BaseTestLoad()
    test_load_impl.run([1, 2, 3])


def test_skip_loading_invalid_entries():
    class TestLoadImpl(BaseTestLoad):
        def __init__(self):
            self.seen = []

        def _prepare(self, entry):
            self.seen.append(entry)

        def _load(self, entry):
            assert entry in self.seen

        def _validate(self, entry):
            return entry != 2

    test_load_impl = TestLoadImpl()
    test_load_impl.run([1, 2, 3])
    assert test_load_impl.seen == [1, 3]


def test_cleanup_called():
    class TestLoadImpl(BaseTestLoad):
        def __init__(self):
            self.cleanup = None

        def _cleanup(self):
            self.cleanup = True

    test_load_impl = TestLoadImpl()
    test_load_impl.run([])
    assert not test_load_impl.cleanup
    test_load_impl.run([], cleanup=True)
    assert test_load_impl.cleanup
