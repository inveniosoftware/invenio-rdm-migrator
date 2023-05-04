# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils module."""

from datetime import datetime


def ts(iso=True, fmt=None):
    """Current timestamp string."""
    dt = datetime.now()
    if fmt:
        return dt.strftime(fmt)
    return dt.isoformat() if iso else dt.timestamp()
