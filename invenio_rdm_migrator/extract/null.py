# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration extract interfaces."""

from .base import Extract


class NullExtract(Extract):
    """Extract class to not read input data."""

    def run(self):
        """Return None only once.

        Subsequent calls to run will raise StopIteration.
        """
        # yield a None value
        yield
