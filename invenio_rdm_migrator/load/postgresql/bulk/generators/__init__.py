# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration PostgreSQL bulk generators module."""

from .existing import ExistingDataTableGenerator
from .single import SingleTableGenerator
from .table import TableGenerator

__all__ = (
    "ExistingDataTableGenerator",
    "SingleTableGenerator",
    "TableGenerator",
)
