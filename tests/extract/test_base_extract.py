# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

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
