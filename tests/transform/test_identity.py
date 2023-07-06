# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity transformation tests."""

import pytest

from invenio_rdm_migrator.transform import (
    IdentityDictKeyMixin,
    IdentityTransform,
    Transform,
)


@pytest.fixture(scope="module")
def transform_with_mixin():
    """Test instance of a transform class with identity mixin"""

    class FixtureTransform(Transform, IdentityDictKeyMixin):
        """Transform fixture class."""

        def _implemented(self, entry):
            return "foo"

        def _transform(self, entry):
            """Transform entry."""
            return {
                "implemented": self._implemented(entry),
                "unimplemented": self._unimplemented(entry),
            }

    return FixtureTransform()


def test_identity_dict_key_mixin(transform_with_mixin):
    input = {"implemented": "test", "unimplemented": "test too"}
    expected = {"implemented": "foo", "unimplemented": "test too"}

    # assert the implemented method has priority over the dictionary value
    # assert the unimplemented method falls back to the dictionary value
    assert transform_with_mixin._transform(input) == expected


def test_identity_transform():
    input = {"implemented": "test", "unimplemented": "test too"}
    expected = {"implemented": "test", "unimplemented": "test too"}

    assert IdentityTransform()._transform(input) == expected
