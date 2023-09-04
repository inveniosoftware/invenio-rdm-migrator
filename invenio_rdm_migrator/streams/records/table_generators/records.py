# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime
from uuid import UUID

import psycopg

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.postgresql.bulk.generators import TableGenerator
from ....logging import Logger
from ....state import STATE
from ...models.communities import RDMParentCommunityMetadata
from ...models.files import FilesObjectVersion
from ...models.pids import PersistentIdentifier
from ...models.records import (
    RDMParentMetadata,
    RDMRecordFile,
    RDMRecordMediaFile,
    RDMRecordMetadata,
)
from .parents import generate_parent_rows
from .references import CommunitiesReferencesMixin


def _is_valid_uuid(value):
    try:
        UUID(value)
        return True
    except Exception:
        return False


def generate_files_uuids(data):
    """Generate uuid for every file in the list.

    Return the transformed list with the generated ids.
    """
    _files = data["record_files"]
    for _file in _files:
        _file["id"] = generate_uuid({})
    return _files


def generate_record_uuid(data):
    """Generate record uuid if not present."""
    _id = data["record"].get("id")
    return _id if _id else generate_uuid(None)


class RDMRecordTableGenerator(TableGenerator, CommunitiesReferencesMixin):
    """RDM Record and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                PersistentIdentifier,
                RDMParentMetadata,
                RDMRecordMetadata,
                RDMParentCommunityMetadata,
                RDMRecordFile,
            ],
            post_load_hooks=[self.insert_media_files],
            pks=[
                ("record.id", generate_record_uuid),
                ("parent.id", generate_uuid),
                ("record.json.pid", generate_recid),
                ("parent.json.pid", generate_recid),
                ("record.parent_id", lambda d: d["parent"]["id"]),
                ("record_files", generate_files_uuids),
            ],
        )

    def _generate_rows(self, data, **kwargs):
        """Generates rows for a record."""
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        record = data.get("record")

        if not record:
            return

        record_pid = record["json"]["pid"]

        # parent
        state_parent = STATE.PARENTS.get(parent["json"]["id"])
        if not state_parent:
            STATE.PARENTS.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "latest_index": record["index"],
                    "latest_id": record["id"],
                },
            )
            yield from generate_parent_rows(parent)
            # parent community
            if "default" in parent["json"]["communities"]:
                parent_def_id = parent["json"]["communities"]["default"]
                parent_comm_id = parent["id"]
                # when a community is deleted, its id is the slug and fails on DB
                # FK expects uuid and not string
                if _is_valid_uuid(parent_def_id) and _is_valid_uuid(parent_comm_id):
                    yield RDMParentCommunityMetadata(
                        community_id=parent_def_id,
                        record_id=parent_comm_id,
                        request_id=None,
                    )
                else:
                    record_id = record["json"]["id"]
                    logger = Logger.get_logger()
                    logger.error(
                        f"Record parent community not migrated. [{record_id=}]. "
                        f"[{parent_comm_id=}], default community [{parent_def_id}]"
                    )
        else:
            if state_parent.get("latest_index") < record["index"]:
                STATE.PARENTS.update(
                    parent["json"]["id"],
                    {
                        "latest_index": record["index"],
                        "latest_id": record["id"],
                    },
                )

        parent_id = state_parent["id"] if state_parent else record["parent_id"]
        # record
        STATE.RECORDS.add(
            record["json"]["id"],  # recid
            {
                "index": record["index"],
                "id": record["id"],  # uuid
                "parent_id": parent_id,  # parent uuid
                "fork_version_id": record["version_id"],
                "pids": record["json"]["pids"],
            },
        )

        yield RDMRecordMetadata(
            id=record["id"],
            json=record["json"],
            created=record["created"],
            updated=record["updated"],
            version_id=record["version_id"],
            index=record["index"],
            bucket_id=record["bucket_id"],
            media_bucket_id=record.get("media_bucket_id"),
            parent_id=parent_id,
            deletion_status="P",
        )
        # recid
        yield PersistentIdentifier(
            id=record_pid["pk"],
            pid_type=record_pid["pid_type"],
            pid_value=record["json"]["id"],
            status=record_pid["status"],
            object_type=record_pid["obj_type"],
            object_uuid=record["id"],
            created=now,
            updated=now,
        )
        # DOI
        if "doi" in record["json"]["pids"]:
            yield PersistentIdentifier(
                id=pid_pk(),
                pid_type="doi",
                pid_value=record["json"]["pids"]["doi"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=record["id"],
                created=now,
                updated=now,
            )
        # OAI
        if "oai" in record["json"]["pids"]:
            yield PersistentIdentifier(
                id=pid_pk(),
                pid_type="oai",
                pid_value=record["json"]["pids"]["oai"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=record["id"],
                created=now,
                updated=now,
            )

        # record files
        record_files = data["record_files"]
        for _file in record_files:
            yield RDMRecordFile(
                id=_file["id"],
                json=_file["json"],
                created=_file["created"],
                updated=_file["updated"],
                version_id=_file["version_id"],
                key=_file["key"],
                record_id=record["id"],
                object_version_id=_file["object_version_id"],
            )

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        if "record" in data:
            # resolve parent communities slug
            parent = data["parent"]
            communities = parent["json"].get("communities")
            if communities:
                self.resolve_communities(communities)

    def insert_media_files(self, db_uri=None):
        """Inserts record media files from buckets and object version."""
        assert db_uri  # should have come from kwargs

        with psycopg.connect(db_uri) as conn:
            # the query needs to be split in 3 parts because the empty jsonb dict
            # would cause problems with the string formatting
            insert = f"""
                INSERT INTO {RDMRecordMediaFile.__tablename__} (
                    id, json, created, updated, version_id, key, record_id, object_version_id
                )
            """
            select = "SELECT gen_random_uuid(), '{}'::jsonb, rrm.created, rrm.updated, 1, fo.key, rrm.id, fo.version_id"
            from_and_join = f"""
                FROM {RDMRecordMetadata.__tablename__} AS rrm
                INNER JOIN {FilesObjectVersion.__tablename__} AS fo
                ON rrm.media_bucket_id = fo.bucket_id AND fo.is_head = 'true'
                WHERE rrm.media_bucket_id IS NOT NULL
            """
            # no return check, will raise if the sql statement fails
            # id and json do not have defaults in DB even though if the programmatic
            # models have them, so they need to be calculated
            conn.execute(insert + select + from_and_join)
