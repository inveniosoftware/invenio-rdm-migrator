# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration extract interfaces."""


from abc import ABC, abstractmethod


class Extract(ABC):
    """Base class for data extraction."""

    @abstractmethod
    def run(self):  # pragma: no cover
        """Yield one element at a time."""
        pass
