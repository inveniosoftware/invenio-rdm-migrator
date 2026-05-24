# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
