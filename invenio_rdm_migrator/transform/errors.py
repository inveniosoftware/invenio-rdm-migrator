# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration transform errors."""


class MultipleActionMatches(Exception):
    """More than one match for one transaction."""

    def __init__(self, tx, matched_classes):
        """Constructor."""
        super().__init__(f"Multiple action matches for {tx}: {matched_classes}")


class NoActionMatch(Exception):
    """No action match for a transaction."""

    def __init__(self, tx):
        """Constructor."""
        super().__init__(f"Could not detect action for {tx}")
