# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from functools import partial

from .base import Transform


class IdentityTransform(Transform):
    """Transform class to yield the received item without change."""

    def _transform(self, entry):
        """Transform entry."""
        return entry
