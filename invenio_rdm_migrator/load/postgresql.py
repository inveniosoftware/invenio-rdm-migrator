# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL load module."""


import contextlib
import csv
import json
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import psycopg
from invenio_records.dictutils import dict_set  # TODO: can we do without?

from .base import Load


def _ts(iso=True):
    """Current timestamp string."""
    dt = datetime.now()
    return dt.isoformat() if iso else dt.timestamp()


def as_csv_row(dc):
    """Serialize a dataclass instance as a CSV-writable row."""
    row = []
    for f in fields(dc):
        val = getattr(dc, f.name)
        if val:
            if issubclass(f.type, (dict,)):
                val = json.dumps(val)
            elif issubclass(f.type, (datetime,)):
                val = val.isoformat()
            elif issubclass(f.type, (UUID,)):
                val = str(val)
        row.append(val)
    return row


def generate_uuid(data):
    """Generate a UUID."""
    return str(uuid4())


class PostgreSQLCopyLoad(Load):  # TODO: abstract SQL from PostgreSQL?
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, table_loads, tmp_dir):
        """Constructor."""
        self.db_uri = db_uri
        self.tmp_dir = Path(tmp_dir) / f"tables{_ts(iso=False)}"
        self.table_loads = table_loads

    def _cleanup(self, db=False):
        """Cleanup csv files and DB after load."""
        for table in self.table_loads:
            table.cleanup(db=db)

    def _prepare(self, entries):
        """Dump entries in csv files for COPY command."""
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        _prepared_tables = []
        for table in self.table_loads:
            # otherwise the generator is exhausted by the first table
            # TODO: nested generators, how expensive is this copy op?
            _prepared_tables.extend(table.prepare(self.tmp_dir, entries=entries))

        return iter(_prepared_tables)  # yield at the end vs yield per table

    def _load(self, table_entries):
        """Bulk load CSV table files.

        Loads the tables in the order given by the generator.
        """
        with psycopg.connect(self.db_uri) as conn:
            for table in table_entries:
                name = table._table_name
                cols = ", ".join([f.name for f in fields(table)])
                fpath = self.tmp_dir / f"{name}.csv"
                if fpath.exists():
                    # total file size for progress logging
                    file_size = fpath.stat().st_size

                    print(f"[{_ts()}] COPY FROM {fpath}")  # TODO: logging
                    with contextlib.ExitStack() as stack:
                        cur = stack.enter_context(conn.cursor())
                        copy = stack.enter_context(
                            cur.copy(f"COPY {name} ({cols}) FROM STDIN (FORMAT csv)")
                        )
                        fp = stack.enter_context(open(fpath, "r"))

                        block_size = 8192

                        def _data_blocks(block_size=8192):
                            data = fp.read(block_size)
                            while data:
                                yield data
                                data = fp.read(block_size)

                        for idx, block in enumerate(_data_blocks(block_size)):
                            if idx % 100:
                                cur_bytes = idx * block_size
                                percentage = (cur_bytes / file_size) * 100
                                progress = (
                                    f"{cur_bytes}/{file_size} ({percentage:.2f}%)"
                                )
                                print(f"[{_ts()}] {name}: {progress}")
                            copy.write(block)
                else:
                    # FIXME: log a WARNING/ERROR
                    print(f"[{_ts()}] {name}: no data to load")
                conn.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        table_entries = self._prepare(entries)
        self._load(table_entries)

        if cleanup:
            self._cleanup()


class TableGenerator(ABC):
    """Create CSV files with table create and inserts."""

    def __init__(self, tables, pks=None):
        """Constructor."""
        self._tables = tables
        self.pks = pks or []

    @abstractmethod
    def _generate_rows(self, **kwargs):
        """Yield generated rows."""
        pass

    @abstractmethod
    def cleanup(self, **kwargs):
        """Cleanup."""
        pass

    def _generate_pks(self, data):
        for path, pk_func in self.pks:
            dict_set(data, path, pk_func(data))

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        pass

    def prepare(self, tmp_dir, entries, **kwargs):
        """Compute rows."""
        # use this context manager to close all opened files at once
        with contextlib.ExitStack() as stack:
            out_files = {}
            for entry in entries:
                # is_db_empty would come in play and make _generate_pks optional
                self._generate_pks(entry)
                # resolve entry references
                self._resolve_references(entry)
                for entry in self._generate_rows(entry):
                    if entry._table_name not in out_files:
                        fpath = tmp_dir / f"{entry._table_name}.csv"
                        out_files[entry._table_name] = csv.writer(
                            stack.enter_context(open(fpath, "w+"))
                        )
                    writer = out_files[entry._table_name]
                    writer.writerow(as_csv_row(entry))

        return self._tables
