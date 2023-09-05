# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils module."""

import json
from datetime import datetime
from uuid import UUID


def ts(iso=True, fmt=None):
    """Current timestamp string."""
    dt = datetime.now()
    if fmt:
        return dt.strftime(fmt)
    return dt.isoformat() if iso else dt.timestamp()


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
        parent = parent.setdefault(key, {})
    parent[keys[-1]] = value
