# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL sequence handling."""


import psycopg


class AlterSequencesMixin:
    """Mixin to update sequences to the latest value."""

    def alter_sequences(self):
        """Query all sequences and update those that were modified."""
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
