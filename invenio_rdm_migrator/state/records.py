# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Records state module."""

from .base import State


class ParentsState(State):
    """Parent record state."""

    def _validate(self, data):
        """Validate data entry."""
        assert "id" in data.keys()  # parent uuid
        assert data["latest_id"] or data["next_draft_id"]
        if data["latest_id"]:
            assert data["latest_index"]

    def add(self, key, data):
        """Add key to the state.

        :param key: the recid of the parent
        """
        key = str(key)  # in case they are numbers
        data.setdefault("latest_id", None)
        data.setdefault("latest_index", 0)
        data.setdefault("next_draft_id", None)
        super().add(key, data)

    def update(self, key, data):
        """Update an entry.

        If it is a record, update the latest index and latest id.
        If it is a draft, update the next draft id.
        """
        key = str(key)  # in case they are numbers
        parent = self._data[key]

        data_idx = data.get("latest_index", 0)  # not present in drafts
        if parent["latest_index"] < data_idx:
            parent["latest_index"] = data_idx
            parent["latest_id"] = data["latest_id"]

        nd_id = data.get("next_draft_id")  # not present in records
        if nd_id:
            assert not parent["next_draft_id"]  # it can only happen once
            parent["next_draft_id"] = data["next_draft_id"]


class RecordsState(State):
    """Record state."""

    def _validate(self, data):
        """Validate data entry."""
        keys = data.keys()
        for value in ["index", "id", "parent_id", "fork_version_id"]:
            assert value in keys
