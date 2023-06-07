# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base state module."""

import tempfile
from io import StringIO

from sqlalchemy import create_engine
from abc import ABC, abstractmethod

from ..logging import Logger
from ..utils import ts


class State(ABC):
    """State interface."""

    def __init__(self, dbpath):
        """Constructor."""

        self.dbpath = dbpath

        start = ts(iso=False)
        logger = Logger.get_logger()
        logger.info(f"Loading state from {dbpath} {ts()}")
        # load file into memory
        disk_file = create_engine(f"sqlite:///{dbpath}").connect()
        # TODO: evaluate using ATTACH to avoid loading to a temporary file
        tempfile = StringIO()
        for line in disk_file.iterdump():
            tempfile.write("%s\n" % line)
        disk_file.close()
        tempfile.seek(0)

        # dump state into in-memory sqlite db
        self.mem_state = create_engine(f"sqlite:///:memory:").connect()
        self.mem_state.executescript(tempfile.read())
        self.mem_state.commit()

        end = ts(iso=False)
        logger.info(f"Finished loading state {ts()}")
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
