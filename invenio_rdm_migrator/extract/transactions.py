# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction extract classes."""

import copy
from dataclasses import dataclass
from typing import Optional, Sequence, Union

import dictdiffer


@dataclass
class Tx:
    """An extracted DB transaction."""

    id: int
    operations: list[dict]  # TODO: we could more narrowly define it later
    commit_lsn: Optional[int] = None

    def as_ops_tuples(self, include=None):
        """Return a list of (table, op_type) tuples."""
        if include is None:
            return [(o["source"]["table"], o["op"]) for o in self.operations]
        else:
            return [
                (table, o["op"])
                for o in self.operations
                if (table := o["source"]["table"]) in include
            ]

    def ops_by(
        self,
        table,
        op_types: Optional[Sequence[str]] = ("C", "U"),
        group_id: Optional[Union[Sequence[str], str, bool]] = True,
        group_key: Optional[Union[Sequence[str], str]] = None,
        filter_unchanged=True,
    ):
        """Return rolled-up and/or grouped table operations."""
        result_by_id = {}
        result = {}

        for op in self.operations:
            if op["source"]["table"] == table and op["op"] in op_types:
                if isinstance(group_id, str):
                    group_id = (group_id,)
                if group_id is True or group_id is None:
                    group_id = sorted(op["key"].keys())
                assert isinstance(group_id, (Sequence, str))
                group_key = group_key or group_id
                if isinstance(group_key, str):
                    group_key = (group_key,)

                if filter_unchanged and op["op"] == "U":
                    ignored_keys = set(group_key) | set(group_id)
                    before, after = self.filter_unchanged(op, ignored_keys)
                else:
                    before = op["before"]
                    after = op["after"]
                data = after or before
                data_id = tuple(data[k] for k in group_id)
                # for one-column PKs just use the single value
                if len(data_id) == 1:
                    data_id = data_id[0]

                result_by_id.setdefault(data_id, {})
                result_by_id[data_id].update(data)

                aggr_data = result_by_id[data_id]
                data_key = tuple(aggr_data.get(k) for k in group_key)
                # for one-column keys just use the single value
                if len(data_key) == 1:
                    data_key = data_key[0]
                result[data_key] = aggr_data
        return result

    def filter_ops(self, table, filter: dict):
        """Return rolled-up and/or grouped table operations."""
        return [
            o
            for o in self.operations
            if o["source"]["table"] == table
            and filter.items() <= (o["after"] or o["before"]).items()
        ]

    @staticmethod
    def filter_unchanged(data, ignored_keys=None):
        before = copy.deepcopy(data["before"])
        after = copy.deepcopy(data["after"])
        ignored_keys = set(ignored_keys or data["key"].keys())
        diff = dictdiffer.diff(before, after, ignore=ignored_keys)
        changed_keys = {key for diff_op, key, _ in diff if diff_op == "change"}
        for key in (before.keys() | after.keys()) - (changed_keys | ignored_keys):
            before.pop(key)
            after.pop(key)
        return before, after
