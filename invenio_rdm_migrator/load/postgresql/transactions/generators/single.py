# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Single row generator."""


from ..operations import Operation
from .row import RowGenerator


class SingleRowGenerator(RowGenerator):
    """Contains only one table to yield."""

    def __init__(self, table, **kwargs):
        """Constructor."""
        assert not isinstance(table, (list, dict))
        super().__init__(**kwargs)
        self.table = table

    def _generate_rows(self, data, op, **kwargs):
        """Yield generated rows."""
        # FIXME: temporary fix to test the microseconds conversion
        # should be moved to a mixin or similar on the transform step
        from datetime import datetime

        if data.get("created"):
            data["created"] = datetime.fromtimestamp(data["created"] / 1_000_000)
        if data.get("updated"):
            data["updated"] = datetime.fromtimestamp(data["updated"] / 1_000_000)

        yield Operation(op, self.table(**data))
