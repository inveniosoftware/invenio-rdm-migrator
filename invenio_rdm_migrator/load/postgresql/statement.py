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

import psycopg

from ...logging import Logger
from ...utils import ts
from ..base import Load


class PostgreSQLExecute(Load):
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, table_generators, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self.table_generators = table_generators

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

    def _post_load(self, model):
        """Post load processing."""

        table_name = model._table_name

        with psycopg.connect(self.db_uri) as conn:
            sequences = conn.execute(
                f"""
                SELECT
                    t.oid::regclass AS table_name,
                    a.attname AS column_name,
                    s.relname AS sequence_name
                FROM pg_class AS t
                    JOIN pg_attribute AS a ON a.attrelid = t.oid
                    JOIN pg_depend AS d ON d.refobjid = t.oid AND d.refobjsubid = a.attnum
                    JOIN pg_class AS s ON s.oid = d.objid
                WHERE
                    {table_name} = t.oid::regclass
                    d.classid = 'pg_catalog.pg_class'::regclass
                    AND d.refclassid = 'pg_catalog.pg_class'::regclass
                    AND d.deptype IN ('i', 'a')
                    AND t.relkind IN ('r', 'P')
                    AND s.relkind = 'S';
                """
            )

            for seq in sequences:
                table_name, column, seq_name = seq
                max_val = conn.execute(f"SELECT MAX({column}) FROM {table_name}")
                max_val = list(max_val)[0][0]  # get actual value from iterator
                if max_val:  # if no updates it returns None
                    conn.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_val}")
                    # does not require commit as it is a ddl op

    def run(self, entries, cleanup=False):
        """Load entries."""
        table_entries = self._prepare(entries)
        self._load(table_entries)
        self._post_load()

        if cleanup:
            self._cleanup()
