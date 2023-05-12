# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base cache module."""

import json
from abc import ABC, abstractmethod

from ...utils import ts


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
