# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL Transaction load operations."""

from dataclasses import dataclass
from enum import Enum

from ..models import Model


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

    def __repr__(self):
        """Eval-friendly enum representation."""
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Operation:
    """SQL operation."""

    type: OperationType
    model: type[Model]
    data: dict
