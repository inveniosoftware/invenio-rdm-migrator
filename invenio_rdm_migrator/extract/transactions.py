# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction extract classes."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Tx:
    """An extracted DB transaction."""

    id: int
    operations: list[dict]  # TODO: we could more narrowly define it later
    commit_lsn: Optional[int] = None

    def as_ops_tuples(self, include=None):
        """Return a list of (table, op_type) tuples."""
        if include is None:
            return [(o["source"]["table"], o["op"]) for o in self.operartions]
        else:
            return [
                (table, o["op"])
                for o in self.operartions
                if (table := o["source"]["table"]) in include
            ]

    def ops_by(self, table, pk: tuple[str] = None):
        """Return rolled-up and/or grouped table operations."""
        res = {}
        for operation in self.operations:
            table_name = operation["source"]["table"]
            before = operation["before"]
            after = operation["after"]
            data = after or before
            if table_name == table:
                if pk:  # group by PK
                    key = tuple(data[k] for k in pk)
                    res.setdefault(key, {})
                    res[key].update(data)
                else:
                    res.update(data)

    def filter_ops(self, table, filter: dict):
        """Return rolled-up and/or grouped table operations."""
        return [
            o
            for o in self.operartions
            if o["source"]["table"] == table
            and filter.items() <= (o["after"] or o["before"]).items()
        ]
