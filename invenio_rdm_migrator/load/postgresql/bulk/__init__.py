# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration PostgreSQL bulk load module."""

from .copy import PostgreSQLCopyLoad

__all__ = ("PostgreSQLCopyLoad",)
