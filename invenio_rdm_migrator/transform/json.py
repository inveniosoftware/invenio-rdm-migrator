# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""JSON field load module."""

import json


class JSONTransformMixin:
    """Loads json fields that are represented as strings."""

    @staticmethod
    def _load_json_fields(fields, data):
        """Load json fields."""
        for field in fields:
            value = data.get(field)
            if value and isinstance(value, str):
                data[field] = json.loads(value)
