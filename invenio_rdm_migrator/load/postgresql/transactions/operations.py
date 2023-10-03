# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL Transaction load operations."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Type

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


def to_db_type(col, val):
    """Convert value to the appropriate DB column type."""
    if issubclass(col.type.python_type, (datetime,)) and isinstance(val, int):
        return datetime.utcfromtimestamp(val / 1_000_000).isoformat()
    return val


@dataclass
class Operation:
    """SQL operation."""

    type: OperationType
    model: Type[Model]
    data: dict

    def as_row_dict(self):
        """Serialize a correctly typed DB row from data."""
        res = {}
        for col in self.model.__mapper__.columns:
            if col.name in self.data:
                res[col.name] = to_db_type(col, self.data[col.name])
        return res

    @property
    def pk_dict(self):
        """Primary keys dict."""
        return {
            col.name: self.data[col.name] for col in self.model.__mapper__.primary_key
        }

    @property
    def pk_clauses(self):
        """Primary keys where clauses."""
        return [col == self.data[col.name] for col in self.model.__mapper__.primary_key]
