# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity transformation tests."""

from invenio_rdm_migrator.transform import IdentityTransform


def test_identity_transform():
    input = {"implemented": "test", "unimplemented": "test too"}
    expected = {"implemented": "test", "unimplemented": "test too"}

    assert IdentityTransform()._transform(input) == expected
