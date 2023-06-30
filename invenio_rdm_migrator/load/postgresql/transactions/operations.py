# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL Transaction load operations."""

from enum import Enum


class OperationType(str, Enum):
    """SQL operation type enumeration."""

    INSERT = "C"
    UPDATE = "U"
    DELETE = "D"

    def __eq__(self, other):
        """Equality test."""
        return self.value == other.upper()

    def __str__(self):
        """Return its value."""
        return self.value


class Operation:
    """SQL operation.

    A transaction is composed by one or more operations.
    """

    def __init__(self, type, obj):
        """Constructor."""
        assert isinstance(type, OperationType)
        self.type = type
        self.obj = obj
