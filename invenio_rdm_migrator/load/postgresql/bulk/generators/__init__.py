# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration PostgreSQL bulk generators module."""

from .existing import ExistingDataTableGenerator
from .single import SingleTableGenerator
from .table import TableGenerator

__all__ = (
    "ExistingDataTableGenerator",
    "SingleTableGenerator",
    "TableGenerator",
)
