# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PIDs cache module."""


from ...load.ids import initialize_pid_pk_value, pid_pk
from .base import Cache


class PIDMaxPKCache(Cache):
    """PID max pk count cache."""

    def __init__(self, filepath=None, validate=False):
        """Constructor."""
        super().__init__(filepath, validate)
        # check if max_pid cache is not empty
        max_value = self._data.get("max_value")
        if max_value:
            # set the initial value of pid_pk() to the max_value cached
            # i.e start generating pks from the cached value and beyond
            initialize_pid_pk_value(max_value)

    def _validate(self, data):
        """Validate data entry."""
        assert isinstance(data, int)

    def add(self, key, data):
        """Method not supported."""
        raise NotImplementedError

    def update(self, key, data):
        """Method not supported."""
        raise NotImplementedError

    def dump(self, filepath):
        """Dump cache data into a json file."""
        max_pid_value = pid_pk.value if hasattr(pid_pk, "value") else pid_pk()
        self._data["max_value"] = max_pid_value  # update to latest current value

        super().dump(filepath)
