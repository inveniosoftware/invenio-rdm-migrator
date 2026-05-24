# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration transform interfaces."""

from .base import Transform


class IdentityTransform(Transform):
    """Transform class to yield the received item without change."""

    def _transform(self, entry):
        """Transform entry."""
        return entry
