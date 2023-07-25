# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction group transform."""

from ..actions.base import TransformAction
from .base import Transform


class Tx(Transform):
    """Transform a transaction group and its items."""

    def _transform(self, entry):
        """Transform action.

        Each action contains the raw transaction data.
        :returns: an instance of LoadAction.
        """
        assert isinstance(entry, TransformAction)
        return entry.transform()
