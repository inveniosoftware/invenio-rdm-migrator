# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Base extract tests."""

import pytest

from invenio_rdm_migrator.extract import Extract


def test_cannot_instantiate_base_class():
    with pytest.raises(TypeError):
        Extract()

    class Test(Extract):
        """Test Extract."""

        pass

    with pytest.raises(TypeError):
        Test()
