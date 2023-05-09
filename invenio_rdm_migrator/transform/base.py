# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from abc import ABC, abstractmethod


class Transform(ABC):
    """Base class for data transformation."""

    @abstractmethod
    def _transform(self, entry):
        """Transform entry."""
        pass

    def run(self, entries, logger=None):
        """Transform and yield one element at a time."""
        for entry in entries:
            try:
                yield self._transform(entry)
            except Exception:
                if logger:
                    logger.error(entry, exc_info=1)
                continue


class Entry(ABC):
    """Base entry class."""

    @abstractmethod
    def transform(self, entry):
        """Transform entry."""
        pass


def drop_nones(data):
    """Recursively drop Nones in dict d and return a new dictionary."""
    dd = {}
    for k, v in data.items():
        if isinstance(v, dict) and v:  # second clause removes empty dicts
            dd[k] = drop_nones(v)
        elif v is not None:
            dd[k] = v
    return dd
