# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration extract interfaces."""


from abc import ABC, abstractmethod


class Extract(ABC):
    """Base class for data extraction."""

    @abstractmethod
    def run(self):  # pragma: no cover
        """Yield one element at a time."""
        pass
