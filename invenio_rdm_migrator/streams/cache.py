# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cache module."""

import json
from abc import ABC, abstractmethod

from ..utils import ts


class Cache(ABC):
    """Cache interface."""

    def __init__(self, filepath=None, validate=False):
        """Constructor."""
        self._data = {}

        if filepath and filepath.exists():  # load cache from file
            start = ts(iso=False)
            print(f"Loading cache from {filepath} {ts()}")
            with open(filepath, "r") as file:
                self._data = json.loads(file.read())

            print(f"Finished loading cache {ts()}")
            if validate:
                print(f"Validating cache {ts()}")
                for _, entry in self._data.items():
                    self._validate(entry)
                print(f"Finished validating cache {ts()}")
            end = ts(iso=False)
            print(f"Cache loading took {end-start} seconds.")

    def dump(self, filepath):
        """Dump cache data into a json file."""
        print(f"Dumping cache to {filepath} {ts()}")
        start = ts(iso=False)

        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(self._data))

        end = ts(iso=False)
        print(f"Finished dumping cache {ts()}")
        print(f"Cache dumping took {end-start} seconds.")

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


class PIDMaxPKCache(Cache):
    """PID max pk count cache."""

    def _validate(self, data):
        """Validate data entry."""
        assert isinstance(data, int)
