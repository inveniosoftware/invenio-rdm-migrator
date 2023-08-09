# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSON field load module."""

import json


class JSONTransformMixin:
    """Loads json fields that are represented as strings."""

    @staticmethod
    def _load_json_fields(fields, data):
        """Load json fields."""
        for field in fields:
            data[field] = json.loads(data[field])
