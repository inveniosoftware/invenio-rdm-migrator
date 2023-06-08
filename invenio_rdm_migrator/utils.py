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


class JSONEncoder(json.JSONEncoder):
    """Ecoder to support UUID inside dictionaries."""

    def default(self, o):
        """Default encoding."""
        if isinstance(o, UUID):
            return str(o)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
