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
from abc import ABC
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from uuid import UUID

import psycopg

from ..logging import Logger
from ..utils import JSONEncoder, ts
from .base import Load


# PORT: from invenio_records.dictutils to avoid having an invenio constraint
# it could cause troubles with sqlalchemy and psycompg version
def parse_lookup_key(lookup_key):
    """Parse a lookup key."""
    if not lookup_key:
        raise KeyError("No lookup key specified")

    # Parse the list of keys
    if isinstance(lookup_key, str):
        keys = lookup_key.split(".")
    elif isinstance(lookup_key, list):
        keys = lookup_key
    else:
        raise TypeError("lookup must be string or list")

    return keys


def dict_set(source, key, value):
    """Set a value into a dict via a dot-notated key."""
    keys = parse_lookup_key(key)
    parent = source
    for key in keys[:-1]:
        if isinstance(key, int):
            parent = parent[key]
        else:
            parent = parent.setdefault(key, {})
    parent[keys[-1]] = value


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


class PostgreSQLCopyLoad(Load):
    """PostgreSQL COPY load."""

    def __init__(
        self,
        db_uri,
        table_generators,
        tmp_dir=None,
        data_dir=None,
        existing_data=False,
        **kwargs,
    ):
        """Constructor.

        :param data_dir: if existing data is true this is the directory from which to
        load the existing csv file, if it is false is the directory where to dump the
        newly created csv files.
        """
        self.db_uri = db_uri
        self.table_generators = table_generators
        # when loading existing data the tmp folder would be the root
        # it is assumed that the csv files of a previous run have been placed there
        self.existing_data = existing_data
        self.data_dir = None
        self.tmp_dir = None
        if existing_data:
            assert data_dir

        assert data_dir or tmp_dir

        if data_dir:
            self.data_dir = Path(data_dir)

        if tmp_dir:
            self.tmp_dir = Path(tmp_dir) / f"tables-{ts(fmt='%Y-%m-%dT%H%M%S')}"

    def _cleanup(self, db=False):
        """Cleanup csv files and DB after load."""
        for table in self.table_generators:
            table.cleanup(db=db)

    def _save_to_csv(self, entries):
        """Save the entries to a csv file."""
        # use this context manager to close all opened files at once
        with contextlib.ExitStack() as stack:
            output_files = {}
            for entry in entries:
                for tg in self.table_generators:
                    tg.prepare(self.tmp_dir, entry, stack, output_files)

            for tg in self.table_generators:
                tg.post_prepare(self.tmp_dir, stack, output_files)

    def _prepare(self, entries):
        """Dump entries in csv files for COPY command."""
        # global overwrite for existing data, e.g. when running a previously run stream
        if not self.existing_data:
            self._save_to_csv(entries)

        prepared_tables = []
        # Needs to preserve order. This logic is very inefficient, maybe and ordered-set
        # or change the data structure of the tables to keep order information and then
        # process it
        for tg in self.table_generators:
            for table in tg.tables:
                existing_data = tg.existing_data or self.existing_data
                if table not in prepared_tables:
                    prepared_tables.append((existing_data, table))

        return iter(prepared_tables)  # yield at the end vs yield per table

    def _load(self, table_entries):
        """Bulk load CSV table files.

        Loads the tables in the order given by the generator.
        """
        logger = Logger.get_logger()

        with psycopg.connect(self.db_uri) as conn:
            for existing_data, table in table_entries:
                name = table._table_name
                cols = ", ".join([f.name for f in fields(table)])
                # local overwrite for existing data
                # e.g. when a table does not need transformation and is already in csv
                fpath = self.data_dir if existing_data else self.tmp_dir
                fpath = fpath / f"{name}.csv"

                if fpath.exists():
                    # total file size for progress logging
                    file_size = fpath.stat().st_size

                    logger.info(f"COPY FROM {fpath}.")
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
                                logger.info(f"{name}: {progress}")
                            copy.write(block)
                else:
                    logger.warning(f"{name}: no data to load.")
                conn.commit()

    def _post_load(self):
        """Post load processing."""
        tables = set()
        for tg in self.table_generators:
            tables = tables.union(set(tg.tables))
            tg.post_load(db_uri=self.db_uri)

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
        self._post_load()

        if cleanup:
            self._cleanup()


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
