# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction group transform."""

from .base import Transform


class Tx(Transform):
    """Transform a transaction group and its items."""

    def __init__(self, table_transform_map):
        """Constructor.

        :param table_transform_map: a dictionary mapping entry transformers to table names.
        """
        # QUESTION: should this dict be a separate class including some validation
        self.table_transform_map = table_transform_map

    def _transform_data(self, table, data):
        """Transform a specific table data based on the defined entry."""
        # e.g. an implementation of RDMRecordEntry when table record_metadata
        entry = self.table_transform_map.get(table)

        return entry._transform(data) if entry else data

    def _transform(self, entry):
        """Transform entry.

        An entry is a dictionary with a list of operations.
        """
        operations = entry["operations"]
        tgroup = {
            # the actual transaction id, useful for debug and error handling
            "tx_id": entry["tx_id"],
            # this information refers to the semantic meaning of the group
            # for example: record metadata update, file upload, draft creation, etc.
            "action": entry["action"],
        }

        _transformed_operations = []
        for operation in operations:
            payload = operation["payload"]
            table_name = payload["source"]["table"]
            _transformed_operations.append(
                {
                    "op": payload["op"],
                    "table": table_name,
                    "data": self._transform_data(table_name, payload["after"]),
                }
            )

        tgroup["operations"] = _transformed_operations

        return tgroup
