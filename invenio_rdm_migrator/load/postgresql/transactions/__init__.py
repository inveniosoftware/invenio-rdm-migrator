# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration PostgreSQL bulk load module."""

from .execute import PostgreSQLTx

__all__ = ("PostgreSQLTx",)
