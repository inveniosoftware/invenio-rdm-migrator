# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration load interfaces."""


from abc import ABC, abstractmethod


class Load(ABC):
    """Base class for data loading."""

    @abstractmethod
    def _validate(self):
        """Validate data before loading."""
        pass

    @abstractmethod
    def _prepare(self):
        """Prepare data for loading."""
        pass

    @abstractmethod
    def _load(self):
        """load data."""
        pass

    @abstractmethod
    def _cleanup(self):
        """Cleanup data after loading."""
        pass

    def run(self, entries, cleanup=False):
        """Load entries."""
        for entry in entries:
            if self._validate(entry):
                self._prepare(entry)
                self._load(entry)

        if cleanup:
            self._cleanup()
