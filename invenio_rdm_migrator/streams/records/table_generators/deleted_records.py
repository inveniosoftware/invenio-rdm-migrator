# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration deleted record load."""

from datetime import datetime

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.postgresql.bulk.generators import TableGenerator
from ....state import STATE
from ...models.pids import PersistentIdentifier
from ...models.records import RDMParentMetadata, RDMRecordMetadata


def generate_record_uuid(data):
    """Generate record uuid if not present."""
    _id = data["record"].get("id")
    return _id if _id else generate_uuid(None)


class RDMDeletedRecordTableGenerator(TableGenerator):
    """RDM Record and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                PersistentIdentifier,
                RDMParentMetadata,
                RDMRecordMetadata,
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
        record = data["record"]

        # Handle parent
        parent_pid_value = parent["json"]["id"]
        state_parent = STATE.PARENTS.get(parent_pid_value)
        if not state_parent:
            if parent_pid_value:
                STATE.PARENTS.add(
                    parent["json"]["id"],  # recid
                    {
                        "id": parent["id"],
                        "latest_index": record["index"],
                        "latest_id": record["id"],
                        "communities": parent.get("communities", {}).get("ids", []),
                    },
                )
                parent_pid = parent["json"]["pid"]
                yield PersistentIdentifier(
                    id=parent_pid["pk"],
                    pid_type=parent_pid["pid_type"],
                    pid_value=parent["json"]["id"],
                    status=parent_pid["status"],
                    object_type=parent_pid["obj_type"],
                    object_uuid=parent["id"],
                    created=now,
                    updated=now,
                )
            parent_doi = parent["json"].get("pids", {}).get("doi")
            if parent_doi and parent_doi["identifier"]:
                yield PersistentIdentifier(
                    id=pid_pk(),
                    pid_type="doi",
                    pid_value=parent_doi["identifier"],
                    status="R",
                    object_type="rec",
                    object_uuid=parent["id"],
                    created=now,
                    updated=now,
                )

            # parent record
            yield RDMParentMetadata(
                id=parent["id"],
                json=parent["json"],
                created=parent["created"],
                updated=parent["updated"],
                version_id=parent["version_id"],
            )
        parent_id = state_parent["id"] if state_parent else record["parent_id"]

        # record
        record_state = STATE.RECORDS.get(record["json"]["id"])
        if not record_state:
            STATE.RECORDS.add(
                record["json"]["id"],  # recid
                {
                    "index": record["index"],
                    "id": record["id"],  # uuid
                    "parent_id": parent_id,  # parent uuid
                    "fork_version_id": record["version_id"],
                    "pids": record["json"].get("pids", {}),
                },
            )
        else:
            # Something is very wrong, we bail out
            return

        yield RDMRecordMetadata(
            id=record["id"],
            json=record["json"],
            created=record["created"],
            updated=record["updated"],
            version_id=record["version_id"],
            index=record["index"],
            bucket_id=record.get("bucket_id"),
            media_bucket_id=record.get("media_bucket_id"),
            parent_id=parent_id,
            deletion_status="D",
        )
        # recid
        record_pid = record["json"]["pid"]
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
        if "doi" in record["json"].get("pids", {}):
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
