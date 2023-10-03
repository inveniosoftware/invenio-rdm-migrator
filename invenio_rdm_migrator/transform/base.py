# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from abc import ABC, abstractmethod
from typing import Optional, Union

import pypeln

from ..logging import Logger


class Transform(ABC):
    """Base class for data transformation."""

    def __init__(self, workers=None, throw=False):
        """Initialize base transform."""
        self._workers = workers
        self._throw = throw

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
                logger.exception(entry, exc_info=True)
                if self._throw:
                    raise

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
                    logger.exception(entry, exc_info=True)
                    if self._throw:
                        raise
                    continue
        else:
            yield from self._multiprocess_transform(entries)


class Entry(ABC):
    """Base entry class."""

    def __init__(self, partial=False):
        """Constructor.

        :param partial: a boolean enabling partial transformations, i.e. missing keys.
        """
        self.partial = partial

    def _load_partial(
        self,
        entry: dict,
        obj: dict,
        keys: list[Union[str, tuple[str, str]]],
        prefix: Optional[str] = None,
    ):
        for key in keys:
            if isinstance(key, tuple):
                key, func_key = key
            else:
                func_key = key
            func = getattr(self, "_" + func_key)
            try:
                val = func(entry)
                if prefix:
                    obj.setdefault(prefix, {})
                    obj[prefix][key] = val
                else:
                    obj[key] = val
            # this might mask nested missing keys, it is still a partial transformation
            # full one (with more validation) should be checked on a record
            except KeyError as ex:
                if not self.partial:
                    raise KeyError(ex)
                pass

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
