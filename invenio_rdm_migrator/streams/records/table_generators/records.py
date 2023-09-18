# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.postgresql.bulk.generators import TableGenerator
from ....state import STATE
from ...models.pids import PersistentIdentifier
from ...models.records import (
    RDMParentMetadata,
    RDMRecordFile,
    RDMRecordMediaFile,
    RDMRecordMetadata,
)
from .parents import generate_parent_rows
from .references import CommunitiesReferencesMixin
from .utils import InsertRecordFiles


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
            ],
            post_load_hooks=[
                InsertRecordFiles(RDMRecordMetadata, RDMRecordFile),
                InsertRecordFiles(
                    RDMRecordMetadata,
                    RDMRecordMediaFile,
                    bucket_fk="media_bucket_id",
                ),
            ],
            pks=[
                ("record.id", generate_record_uuid),
                ("parent.id", generate_uuid),
                ("record.json.pid", generate_recid),
                ("parent.json.pid", generate_recid),
                ("record.parent_id", lambda d: d["parent"]["id"]),
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

        # Handle parent
        state_parent = STATE.PARENTS.get(parent["json"]["id"])
        if not state_parent:
            STATE.PARENTS.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "latest_index": record["index"],
                    "latest_id": record["id"],
                    "communities": parent.get("communities", {}).get("ids", []),
                },
            )
            yield from generate_parent_rows(parent)
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

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        if "record" in data:
            # resolve parent communities slug
            parent = data["parent"]
            communities = parent["json"].get("communities")
            if communities:
                self.resolve_communities(communities)
