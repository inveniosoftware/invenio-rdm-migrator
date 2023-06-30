# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration PostgreSQL base row generator."""

from ...generators import PostgreSQLGenerator


class RowGenerator(PostgreSQLGenerator):
    """Iterate in memory the rows to insert/update/delete."""

    def prepare(self, entry, **kwargs):
        """Compute rows."""
        # is_db_empty would come in play and make _generate_pks optional
        self._generate_pks(entry)
        # resolve entry references
        self._resolve_references(entry)
        yield from self._generate_rows(entry, **kwargs)
