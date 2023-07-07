# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base PostgreSQL generator."""

from abc import ABC, abstractmethod

from ...logging import Logger


# PORT: from invenio_records.dictutils to avoid having an invenio constraint
# it could cause troubles with sqlalchemy and psycompg version
def parse_lookup_key(lookup_key):
    """Parse a lookup key."""
    if not lookup_key:
        raise KeyError("No lookup key specified")

    # Parse the list of keys
    if isinstance(lookup_key, str):
        keys = lookup_key.split(".")
    elif isinstance(lookup_key, list):
        keys = lookup_key
    else:
        raise TypeError("lookup must be string or list")

    return keys


def dict_set(source, key, value):
    """Set a value into a dict via a dot-notated key."""
    keys = parse_lookup_key(key)
    parent = source
    for key in keys[:-1]:
        if isinstance(key, int):
            parent = parent[key]
        else:
            parent = parent.setdefault(key, {})
    parent[keys[-1]] = value


class PostgreSQLGenerator(ABC):
    """PostgreSQL generator interface.

    Prepares the data to be consumed by a Load class.
    """

    def __init__(self, pks=None, post_load_hooks=None):
        """Constructor."""
        self.post_load_hooks = post_load_hooks or []
        self.pks = pks or []

    def _generate_rows(self, **kwargs):
        """Yield generated rows."""
        # raises an error but does not force an implementation
        # e.g. when `prepare` is overwritten, _generate_rows is not required
        raise NotImplementedError

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass

    def _generate_pks(self, data, create=False):
        keys = data.keys()
        for path, pk_func in self.pks:
            try:
                root = path.split(".")[0]
                # avoids creating e.g. "record" in a draft and generating a recid + uuid
                if create or root in keys:
                    dict_set(data, path, pk_func(data))
            except KeyError:
                logger = Logger.get_logger()
                logger.exception(f"Path {path} not found on record", exc_info=1)

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        pass

    @abstractmethod
    def prepare(self, **kwargs):
        """Prepare data for loading."""
        pass

    def post_prepare(self, **kwargs):
        """Create rows after iterating over the entries."""
        pass

    def post_load(self, **kwargs):
        """Create rows after iterating over the entries."""
        for hook in self.post_load_hooks:
            hook(**kwargs)
