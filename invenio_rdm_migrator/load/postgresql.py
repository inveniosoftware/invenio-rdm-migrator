# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL load module."""


import contextlib
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from pathlib import Path

import psycopg
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
            elif issubclass(f.type, (uuid.UUID,)):
                val = str(val)
        row.append(val)
    return row


class PostgreSQLCopyLoad(Load):  # TODO: abstract SQL from PostgreSQL?
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, table_loads, output_path):
        """Constructor."""
        self.db_uri = db_uri
        self.output_dir = Path(output_path) / f"data/tables{_ts(iso=False)}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._table_loads = table_loads

    def _cleanup(self, db=False):
        """Cleanup csv files and DB after load."""
        for table in self.tables:
            table.cleanup_files(db)

    def _prepare(self, entries):
        """Dump entries in csv files for COPY command."""

        _prepared_tables = []
        for table in self._table_loads:
            # otherwise the generator is exahusted by the first table
            # TODO: nested generators, how expensive is this copy op?
            _prepared_tables.extend(
                table.prepare(self.output_dir, entries=entries)
            )
        
        return iter(_prepared_tables)  # yield at the end vs yield per table

    def _load(self, table_entries):
        """Bulk load CSV table files.

        Loads the tables in the order given by the generator.
        """
        with psycopg.connect(self.db_uri) as conn:
            for table in table_entries:
                name = table._table_name
                cols = ", ".join([f.name for f in fields(table)])
                fpath = self.output_dir / f"{name}.csv"
                file_size = fpath.stat().st_size  # total file size for progress logging

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
                            progress = f"{cur_bytes}/{file_size} ({percentage:.2f}%)"
                            print(f"[{_ts()}] {name}: {progress}")
                        copy.write(block)
                conn.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        table_entries = self._prepare(entries) 
        self._load(table_entries)

        if cleanup:
            self._cleanup()


class DBTableLoad(ABC):
    """Create CSV files with table create and inserts."""

    def __init__(self, tables):
        """Constructor."""
        self._tables = tables

    @abstractmethod
    def _cleanup_db(self):
        """Cleanup DB after load."""
        pass

    @abstractmethod
    def _cleanup_files(self):
        """Cleanup files after load."""
        pass

    @abstractmethod
    def _generate_db_tuples(self, **kwargs):
        """Yield generated tuples."""
        pass

    @abstractmethod
    def prepare(self, output_dir, **kwargs):
        """Compute rows."""
        pass

    def cleanup(self, db, **kwargs):
        """Cleanup."""
        self._cleanup_files()

        if db:  # DB cleanup is not always desired
            self._cleanup_db()