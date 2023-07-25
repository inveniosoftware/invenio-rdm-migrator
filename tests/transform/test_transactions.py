# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity transaction transformation tests."""


from invenio_rdm_migrator.actions import LoadAction, TransformAction
from invenio_rdm_migrator.transform import Tx


class TestLoadAction(LoadAction):
    """Test load action."""

    name = "test-load"

    def _generate_rows(self, **kwargs):  # pragma: no cover
        """Yield generated rows."""
        yield


class TestTransformAction(TransformAction):
    """Test transform action."""

    name = "test-transform"
    mapped_cls = TestLoadAction

    def fingerprint(self):  # pragma: no cover
        """Checks if the data corresponds with that required by the action."""
        return True

    def _transform_data(self):  # pragma: no cover
        """Transforms the data and returns an instance of the mapped_cls."""
        return {}


def test_transform_returns_load_action():
    tx = Tx()
    action = TestTransformAction(1, [])
    assert isinstance(tx._transform(action), LoadAction)
