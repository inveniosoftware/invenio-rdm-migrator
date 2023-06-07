# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities state module."""

from uuid import UUID

from .base import State


class CommunitiesState(State):
    """Communities state."""

    def _validate(self, data):
        """Validate data entry."""
        try:
            UUID(data)
        except ValueError:
            raise AssertionError

    def get(self, key):
        """Get data from the state."""
        key = str(key)  # in case they are numbers
        return self._data.get(key)
