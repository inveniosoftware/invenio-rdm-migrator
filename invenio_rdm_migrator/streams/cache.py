# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cache module."""

from abc import ABC, abstractmethod


class Cache(ABC):
    """Cache interface."""

    def __init__(self):
        """Constructor."""
        self._data = {}

    def get(self, key):
        """Get data from the cache."""
        key = str(key)  # in case they are numbers
        return self._data.get(key, {})

    def all(self):
        """Get all the data from the cache."""
        return self._data.values()

    @abstractmethod
    def _validate(self, data):
        """Validate data entry."""
        pass

    def add(self, key, data):
        """Add key to the cache.

        :param key: recid
        """
        key = str(key)  # in case they are numbers
        assert not self._data.get(key)
        self._validate(data)
        self._data[key] = data

    def update(self, key, data):
        """Update an entry."""
        key = str(key)  # in case they are numbers
        assert self._data.get(key)
        self._validate(data)
        self._data[key] = data


class ParentsCache(Cache):
    """Parent record cache."""

    def _validate(self, data):
        """Validate data entry."""
        assert "id" in data.keys()  # parent uuid
        assert data["latest_id"] or data["next_draft_id"]
        if data["latest_id"]:
            assert data["latest_index"]

    def add(self, key, data):
        """Add key to the cache.

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


class RecordsCache(Cache):
    """Record cache."""

    def _validate(self, data):
        """Validate data entry."""
        keys = data.keys()
        for value in ["index", "id", "parent_id", "fork_version_id"]:
            assert value in keys
