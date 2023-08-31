# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base table generator."""

import csv
from dataclasses import fields
from datetime import datetime
from uuid import UUID

import orjson

from ...generators import PostgreSQLGenerator


def as_csv_row(dc):
    """Serialize a dataclass instance as a CSV-writable row."""
    row = []
    for f in fields(dc):
        val = getattr(dc, f.name)
        if val:
            if issubclass(f.type, (dict,)):
                val = orjson.dumps(val).decode("utf-8")
            elif issubclass(f.type, (datetime,)):
                val = val.isoformat()
            elif issubclass(f.type, (UUID,)):
                val = str(val)
        row.append(val)
    return row


class TableGenerator(PostgreSQLGenerator):
    """Create CSV files with table create and inserts."""

    def __init__(self, tables, pks=None, post_load_hooks=None, existing_data=False):
        """Constructor."""
        super().__init__(pks, post_load_hooks)
        self.tables = tables
        self.existing_data = existing_data

    def prepare(self, tmp_dir, entry, stack, output_files, create=False, **kwargs):
        """Compute rows."""
        if not self.existing_data:
            # is_db_empty would come in play and make _generate_pks optional
            self._generate_pks(entry, create)
            # resolve entry references
            self._resolve_references(entry)

            for entry in self._generate_rows(entry):
                if entry.__tablename__ not in output_files:
                    fpath = tmp_dir / f"{entry.__tablename__}.csv"
                    output_files[entry.__tablename__] = csv.writer(
                        stack.enter_context(open(fpath, "w+"))
                    )
                writer = output_files[entry.__tablename__]
                writer.writerow(as_csv_row(entry))
