# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base state module."""
import json
from abc import ABC, abstractmethod

from ..logging import Logger
from ..utils import ts


class State(ABC):
    """State interface."""

    def __init__(self, filepath=None, validate=False):
        """Constructor."""
        self._data = {}
        logger = Logger.get_logger()
        if filepath and filepath.exists():  # load state from file
            start = ts(iso=False)
            logger.info(f"Loading state from {filepath} {ts()}")
            with open(filepath, "r") as file:
                self._data = json.loads(file.read())

            logger.info(f"Finished loading state {ts()}")
            if validate:
                logger.info(f"Validating state {ts()}")
                for _, entry in self._data.items():
                    self._validate(entry)
                logger.info(f"Finished validating state {ts()}")
            end = ts(iso=False)
            logger.info(f"State loading took {end-start} seconds.")

    def dump(self, filepath):
        """Dump state data into a json file."""
        logger = Logger.get_logger()
        logger.info(f"Dumping state to {filepath} {ts()}")
        start = ts(iso=False)

        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(self._data))

        end = ts(iso=False)
        logger.info(f"Finished dumping state {ts()}")
        logger.info(f"State dumping took {end-start} seconds.")

    def get(self, key):
        """Get data from the state."""
        key = str(key)  # in case they are numbers
        return self._data.get(key, {})

    def all(self):
        """Get all the data from the state."""
        return self._data.values()

    @abstractmethod
    def _validate(self, data):
        """Validate data entry."""
        pass

    def add(self, key, data):
        """Add key to the state.

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
