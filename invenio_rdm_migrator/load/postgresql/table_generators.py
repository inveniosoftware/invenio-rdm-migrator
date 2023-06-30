# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Table generator module."""

import csv
import json
from abc import ABC
from dataclasses import fields
from datetime import datetime
from uuid import UUID

from invenio_records.dictutils import dict_set

from ...logging import Logger
from ...utils import JSONEncoder


def as_csv_row(dc):
    """Serialize a dataclass instance as a CSV-writable row."""
    row = []
    for f in fields(dc):
        val = getattr(dc, f.name)
        if val:
            if issubclass(f.type, (dict,)):
                val = json.dumps(val, cls=JSONEncoder)
            elif issubclass(f.type, (datetime,)):
                val = val.isoformat()
            elif issubclass(f.type, (UUID,)):
                val = str(val)
        row.append(val)
    return row


class TableGenerator(ABC):
    """Create CSV files with table create and inserts."""

    def __init__(self, tables, pks=None, post_load_hooks=None, existing_data=False):
        """Constructor."""
        self.tables = tables
        self.existing_data = existing_data
        self.post_load_hooks = post_load_hooks or []
        self.pks = pks or []

    def _generate_rows(self, **kwargs):
        """Yield generated rows."""
        # raises an error but does not force an implementation
        # e.g. when `prepare` is overwritten, _generate_rows is not required
        raise NotImplementedError

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass

    def _generate_pks(self, data, create=False):
        keys = data.keys()
        for path, pk_func in self.pks:
            try:
                root = path.split(".")[0]
                # avoids creating e.g. "record" in a draft and generating a recid + uuid
                if create or root in keys:
                    dict_set(data, path, pk_func(data))
            except KeyError:
                logger = Logger.get_logger()
                logger.error(f"Path {path} not found on record")

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        pass

    def prepare(self, tmp_dir, entry, stack, output_files, **kwargs):
        """Compute rows."""
        if not self.existing_data:
            # is_db_empty would come in play and make _generate_pks optional
            self._generate_pks(entry, kwargs.get("create", False))
            # resolve entry references
            self._resolve_references(entry)

            tmp_dir.mkdir(parents=True, exist_ok=True)
            for entry in self._generate_rows(entry):
                if entry._table_name not in output_files:
                    fpath = tmp_dir / f"{entry._table_name}.csv"
                    output_files[entry._table_name] = csv.writer(
                        stack.enter_context(open(fpath, "w+"))
                    )
                writer = output_files[entry._table_name]
                writer.writerow(as_csv_row(entry))

    def post_prepare(self, tmp_dir, stack, output_files, **kwargs):
        """Create rows after iterating over the entries."""
        pass

    def post_load(self, **kwargs):
        """Create rows after iterating over the entries."""
        for hook in self.post_load_hooks:
            hook(**kwargs)


class ExistingDataTableGenerator(TableGenerator):
    """Table generator to import data directly from existing data.

    This is useful when the data_dir already contain the files (e.g. csv) with
    the contents to be imported, for example from a previous migration run. Using
    this table generator the Extract and Transform steps can be skipped.
    """

    def __init__(self, tables, pks=None, post_load_hooks=None):
        """Constructor."""
        super().__init__(tables, pks=None, post_load_hooks=None, existing_data=True)


class SingleTableGenerator(TableGenerator):
    """Yields one row of the specified model per entry."""

    def __init__(self, table, pks=None, post_load_hooks=None):
        """Constructor."""
        assert not isinstance(table, (list, dict))

        super().__init__(tables=[table], pks=pks, post_load_hooks=post_load_hooks)

    def _generate_rows(self, data, **kwargs):
        """Yield generated rows."""
        table = self.tables[0]
        yield table(**data)
