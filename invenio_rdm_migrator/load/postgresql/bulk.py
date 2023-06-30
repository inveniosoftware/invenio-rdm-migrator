# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL COPY load."""


import contextlib
from dataclasses import fields
from pathlib import Path

import psycopg2

from ...logging import Logger
from ...utils import ts
from ..base import Load


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

        with psycopg2.connect(self.db_uri) as conn:
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

        with psycopg2.connect(self.db_uri) as conn:
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
