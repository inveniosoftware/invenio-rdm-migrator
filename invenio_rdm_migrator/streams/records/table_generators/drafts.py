# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration draft table load module."""

from datetime import datetime
from functools import partial

from ....load.ids import generate_recid, generate_uuid
from ....load.postgresql.bulk.generators import TableGenerator
from ....state import STATE
from ...models.pids import PersistentIdentifier
from ...models.records import (
    RDMDraftFile,
    RDMDraftMediaFile,
    RDMDraftMetadata,
    RDMParentMetadata,
)
from .parents import generate_parent_rows
from .references import CommunitiesReferencesMixin, PIDsReferencesMixin
from .utils import InsertRecordFiles


class RDMDraftTableGenerator(
    TableGenerator,
    CommunitiesReferencesMixin,
    PIDsReferencesMixin,
):
    """RDM Record and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                RDMDraftMetadata,
                RDMParentMetadata,
                PersistentIdentifier,
            ],
            post_load_hooks=[
                InsertRecordFiles(RDMDraftMetadata, RDMDraftFile),
                InsertRecordFiles(
                    RDMDraftMetadata,
                    RDMDraftMediaFile,
                    bucket_fk="media_bucket_id",
                ),
            ],
            pks=[
                ("draft.id", generate_uuid),
                ("parent.id", generate_uuid),
                ("draft.json.pid", partial(generate_recid, status="N")),
                ("parent.json.pid", generate_recid),
                ("draft.parent_id", lambda d: d["parent"]["id"]),
            ],
        )

    def _generate_rows(self, data, **kwargs):
        """Generates rows for a record."""
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        draft = data.get("draft")
        if not draft:
            return

        recid = draft["json"]["id"]
        forked_published = STATE.RECORDS.get(recid)
        state_parent = STATE.PARENTS.get(parent["json"]["id"])

        if not state_parent:
            STATE.PARENTS.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "next_draft_id": draft["id"],
                },
            )
            # drafts have a parent on save
            # on the other hand there is no community parent/request
            yield from generate_parent_rows(parent)
        # if there is a parent but there is no record it means that it is a
        # draft of a new version
        elif state_parent and not forked_published:
            STATE.PARENTS.update(parent["json"]["id"], {"next_draft_id": draft["id"]})

        # if its a draft of a published record, its parent should be parent id
        # if its a new version, its parent should be the one of the previous version
        # otherwise is a new parent (new record, new draft...)
        parent_id = state_parent["id"] if state_parent else draft["parent_id"]
        if forked_published:
            parent_id = forked_published["parent_id"]

        draft_id = forked_published.get("id") or draft["id"]
        # all drafts have a bucket due to the `post_create` hook on the files sysfield
        STATE.BUCKETS.add(draft["bucket_id"], {"draft_id": draft_id})

        yield RDMDraftMetadata(
            id=draft_id,
            json=draft["json"],
            created=draft["created"],
            updated=draft["updated"],
            version_id=draft["version_id"],
            index=forked_published.get("index") or draft["index"],
            bucket_id=draft["bucket_id"],
            media_bucket_id=draft.get("media_bucket_id"),
            parent_id=parent_id,
            expires_at=draft["expires_at"],
            fork_version_id=forked_published.get("fork_version_id")
            or draft["fork_version_id"],
        )

        # if there is a record in the state it means both recid and doi were already
        # processed in the records table generator, a duplicate would violate unique
        # constraints and cause the load to fail.
        if not forked_published:
            # recid
            record_pid = draft["json"]["pid"]
            yield PersistentIdentifier(
                id=record_pid["pk"],
                pid_type=record_pid["pid_type"],  # in drafts are recid
                pid_value=draft["json"]["id"],
                status=record_pid["status"],
                object_type=record_pid["obj_type"],
                object_uuid=draft["id"],
                created=now,
                updated=now,
            )
        # we don't emit doi Persistentidentifier for drafts as either they have already
        # one from records or have an external doi that is registered on publish
        # draft files are a post_hook

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        # resolve parent communities slug
        draft = data.get("draft")
        if draft:
            parent = data["parent"]
            communities = parent["json"].get("communities")
            if communities:
                self.resolve_communities(communities)
            self.resolve_draft_pids(draft)
