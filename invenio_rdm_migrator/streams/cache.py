# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record streams cache."""


class ParentCache:
    """Parent record cache."""

    def __init__(self):
        """Constructor."""
        self._data = {}

    def add(self, key, data):
        """Add key to the cache.

        :param key: the recid of the parent
        """
        data.setdefault("latest_id", None)
        data.setdefault("latest_index", 0)
        data.setdefault("latest_draft_index", 0)
        data.setdefault("next_draft_id", None)

        assert "id" in data.keys()  # parent uuid
        assert data["latest_id"] or data["next_draft_id"]
        if data["latest_id"]:
            assert data["latest_index"]

        self._data[key] = data

    def _update_record(self, parent, data):
        """Update record information."""
        if parent["latest_index"] < data["index"]:
            parent["latest_index"] = data["index"]
            parent["latest_id"] = data["id"]

        # if there is a larger version the draft is old
        if parent["latest_draft_index"] < data["index"]:
            parent["next_draft_id"] = None

    def _update_draft(self, parent, data):
        """Update a draft information."""
        if (
            parent["latest_index"] < data["index"]
            and parent["latest_draft_index"] < data["index"]
        ):
            parent["latest_draft_index"] = data["index"]
            parent["next_draft_id"] = data["id"]

    def update(self, key, data):
        """Update an entry."""
        parent = self._data[key]
        if not data.get("next_draft_id"):
            self._update_record(parent, data)
        else:
            self._update_draft(parent, data)

    def get(self, key):
        """Get data from the cache."""
        return self._data.get(key, {})

    def all(self):
        """Get all the data from the cache."""
        return self._data.values()
