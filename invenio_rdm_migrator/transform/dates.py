# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSON field load module."""

from datetime import datetime


class DatetimeMixin:
    """Transform integers to datetime.

    Assumes no timezone (UTC).
    """

    @staticmethod
    def _microseconds_to_isodate(data, fields):
        """Transform int to datetime."""
        for field in fields:
            value = data.get(field)
            if isinstance(value, int):  # would also ignore None values
                data[field] = datetime.utcfromtimestamp(value / 1_000_000).isoformat()

    @staticmethod
    def _milliseconds_to_isodate(data, fields):
        """Transform int to datetime."""
        for field in fields:
            value = data.get(field)
            if isinstance(value, int):  # would also ignore None values
                data[field] = datetime.utcfromtimestamp(value / 1_000).isoformat()
