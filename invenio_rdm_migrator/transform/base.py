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

    def run(self, entries):
        """Transform and yield one element at a time."""
        for entry in entries:
            yield self._transform(entry)


class Entry(ABC):
    """Base entry class."""

    @abstractmethod
    def transform(self, entry):
        """Transform entry."""
        pass
