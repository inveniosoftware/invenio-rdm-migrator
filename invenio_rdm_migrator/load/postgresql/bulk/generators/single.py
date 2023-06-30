# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Single table generator module."""

from .table import TableGenerator


class SingleTableGenerator(TableGenerator):
    """Contains only one table to yield."""

    def __init__(self, table, pks=None, post_load_hooks=None):
        """Constructor."""
        assert not isinstance(table, (list, dict))

        super().__init__(tables=[table], pks=pks, post_load_hooks=post_load_hooks)

    def _generate_rows(self, data, **kwargs):
        """Yield generated rows."""
        table = self.tables[0]
        yield table(**data)
