# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Identity transformation tests."""

from invenio_rdm_migrator.transform import IdentityTransform


def test_identity_transform():
    input = {"implemented": "test", "unimplemented": "test too"}
    expected = {"implemented": "test", "unimplemented": "test too"}

    assert IdentityTransform()._transform(input) == expected
