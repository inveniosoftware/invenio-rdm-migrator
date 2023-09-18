# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record table generator utilities."""

import psycopg

from ...models.files import FilesObjectVersion


class InsertRecordFiles:
    """Table generator post-hook for inserting record files from object versions."""

    def __init__(self, record_model, file_model, bucket_fk="bucket_id"):
        """Constructor."""
        self.record_model = record_model
        self.file_model = file_model
        self.bucket_fk = bucket_fk

    def __call__(self, db_uri=None):
        """Inserts record files from buckets and object versions."""
        assert db_uri  # should have come from kwargs

        with psycopg.connect(db_uri) as conn:
            # the query needs to be split in 3 parts because the empty jsonb dict
            # would cause problems with the string formatting
            insert = f"""
                INSERT INTO {self.file_model.__tablename__} (
                    id, json, created, updated, version_id, key, record_id, object_version_id
                )
            """
            select = "SELECT gen_random_uuid(), '{}'::jsonb, record.created, record.updated, 1, fo.key, record.id, fo.version_id"
            from_and_join = f"""
                FROM {self.record_model.__tablename__} AS record
                INNER JOIN {FilesObjectVersion.__tablename__} AS fo
                ON record.{self.bucket_fk} = fo.bucket_id AND fo.is_head = 'true'
                WHERE record.{self.bucket_fk} IS NOT NULL
            """
            # no return check, will raise if the sql statement fails
            # id and json do not have defaults in DB even though if the programmatic
            # models have them, so they need to be calculated
            conn.execute(insert + select + from_and_join)
