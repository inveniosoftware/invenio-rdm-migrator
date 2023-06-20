# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration extract interfaces."""

from .base import Extract


class IdentityExtract(Extract):
    """Extract class to not read input data."""

    def run(self):
        """Yield one element at a time."""
        # yield a dummy value
        yield
