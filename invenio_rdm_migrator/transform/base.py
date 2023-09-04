# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from abc import ABC, abstractmethod

import pypeln

from ..logging import Logger


class Transform(ABC):
    """Base class for data transformation."""

    def __init__(self, workers=None):
        """Initialize base transform."""
        self._workers = workers

    @abstractmethod
    def _transform(self, entry):  # pragma: no cover
        """Transform entry.

        :returns: a transformed entry, not an iterator.
        """
        pass

    def _multiprocess_transform(self, entries):
        def _transform(entry):
            try:
                return self._transform(entry)
            except Exception:
                logger = Logger.get_logger()
                logger.exception(entry, exc_info=1)

        for result in pypeln.process.map(
            _transform,
            entries,
            workers=self._workers,
            maxsize=self._workers * 100,
        ):
            if result:
                yield result

    def run(self, entries):
        """Transform and yield one element at a time."""
        if self._workers is None:
            for entry in entries:
                try:
                    yield self._transform(entry)
                except Exception:
                    logger = Logger.get_logger()
                    logger.exception(entry, exc_info=1)
                    continue
        else:
            yield from self._multiprocess_transform(entries)


class Entry(ABC):
    """Base entry class."""

    @abstractmethod
    def transform(self, entry):  # pragma: no cover
        """Transform entry."""
        pass


def drop_nones(data):
    """Recursively drop Nones in dict d and return a new dictionary."""
    dd = {}
    for k, v in data.items():
        if isinstance(v, dict) and v:  # second clause removes empty dicts
            dd[k] = drop_nones(v)
        elif v is not None:
            dd[k] = v
    return dd
