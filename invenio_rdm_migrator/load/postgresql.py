# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
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
from uuid import UUID

import psycopg
from invenio_records.dictutils import dict_set  # TODO: can we do without?

from ..utils import ts
from .base import Load


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


class PostgreSQLCopyLoad(Load):
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, table_generators, tmp_dir):
        """Constructor."""
        self.db_uri = db_uri
        self.tmp_dir = Path(tmp_dir) / f"tables-{ts(fmt='%Y-%m-%dT%H%M%S')}"
        self.table_generators = table_generators

    def _cleanup(self, db=False):
        """Cleanup csv files and DB after load."""
        for table in self.table_generators:
            table.cleanup(db=db)

    def _prepare(self, entries):
        """Dump entries in csv files for COPY command."""
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        # use this context manager to close all opened files at once
        with contextlib.ExitStack() as stack:
            output_files = {}
            for entry in entries:
                for tg in self.table_generators:
                    tg.prepare(self.tmp_dir, entry, stack, output_files)

            for tg in self.table_generators:
                tg.post_prepare(self.tmp_dir, stack, output_files)

        prepared_tables = []
        # FIXME: needs to preserve order
        # the logic is very inefficient, maybe and ordered-set
        # or change the data structure of tables to keep order information
        # and hten process it
        for tg in self.table_generators:
            for table in tg.tables:
                if table not in prepared_tables:
                    prepared_tables.append(table)

        return iter(prepared_tables)  # yield at the end vs yield per table

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

                    print(f"[{ts()}] COPY FROM {fpath}")  # TODO: logging
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
                                print(f"[{ts()}] {name}: {progress}")
                            copy.write(block)
                else:
                    # FIXME: log a WARNING/ERROR
                    print(f"[{ts()}] {name}: no data to load")
                conn.commit()

    def _post_load(self):
        """Post load processing."""
        tables = set()
        for tg in self.table_generators:
            tables = tables.join(set(tg.tables))

        with psycopg.connect(self.db_uri) as conn:
            sequences = conn.execute(
                """
                SELECT
                    t.oid::regclass AS table_name,
                    a.attname AS column_name,
                    s.relname AS sequence_name
                FROM pg_class AS t
                    JOIN pg_attribute AS a ON a.attrelid = t.oid
                    JOIN pg_depend AS d ON d.refobjid = t.oid AND d.refobjsubid = a.attnum
                    JOIN pg_class AS s ON s.oid = d.objid
                WHERE
                    d.classid = 'pg_catalog.pg_class'::regclass
                    AND d.refclassid = 'pg_catalog.pg_class'::regclass
                    AND d.deptype IN ('i', 'a')
                    AND t.relkind IN ('r', 'P')
                    AND s.relkind = 'S';
                """
            )

            for seq in sequences:
                table_name, column, seq_name = seq
                if table_name in tables:
                    max_val = conn.execute(f"SELECT MAX({column}) FROM {table_name}")
                    max_val = list(max_val)[0][0]  # get actual value from iterator
                    if max_val:  # if no updates it returns None
                        conn.execute(
                            f"ALTER SEQUENCE {seq_name} RESTART WITH {max_val}"
                        )
                        # does not require commit as it is a ddl op

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
        self.tables = tables
        self.pks = pks or []

    @abstractmethod
    def _generate_rows(self, **kwargs):
        """Yield generated rows."""
        pass

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
                print(f"Path {path} not found on record")

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        pass

    def prepare(self, tmp_dir, entry, stack, output_files, **kwargs):
        """Compute rows."""
        # is_db_empty would come in play and make _generate_pks optional
        self._generate_pks(entry, kwargs.get("create", False))
        # resolve entry references
        self._resolve_references(entry)
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
