# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration load module."""

from .base import Load
from .postgresql import PostgreSQLCopyLoad, TableGenerator

__all__ = (
    "Load",
    "PostgreSQLCopyLoad",
    "TableGenerator",
)
