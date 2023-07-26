# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration drafts row load module."""

from datetime import datetime
from functools import partial

from ...actions import LoadAction
from ...load.ids import generate_pk, generate_recid, generate_uuid
from ...load.postgresql.transactions.operations import Operation, OperationType
from ..models.files import FilesBucket
from ..models.pids import PersistentIdentifier
from ..models.records import RDMDraftMetadata, RDMVersionState
from ..records.table_generators.parents import generate_parent_rows  # FIXME: move
from ..records.table_generators.references import (
    CommunitiesReferencesMixin,
    PIDsReferencesMixin,
)


class RDMDraftCreateAction(LoadAction, CommunitiesReferencesMixin, PIDsReferencesMixin):
    """RDM draft creation."""

    name = "create-draft"

    def __init__(
        self,
        tx_id,
        pid,
        bucket,
        draft,
        parent,
        parents_state,
        records_state,
        communities_state,
        pids_state,
    ):
        """Constructor."""
        super().__init__(
            tx_id,
            pks=[
                ("pid", "id", generate_pk),
                ("draft", "id", generate_uuid),
                ("parent", "id", generate_uuid),
                ("parent", "json.pid", generate_recid),
                ("draft", "json.pid", partial(generate_recid, status="N")),
            ],
        )
        assert pid and bucket and draft and parent  # i.e. not None as parameter
        self.pid = pid
        self.bucket = bucket
        self.draft = draft
        self.parent = parent
        # state related
        self.parents_state = parents_state
        self.records_state = records_state
        self.communities_state = communities_state
        self.pids_state = pids_state

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        yield from self._generate_pid_rows(**kwargs)
        yield from self._generate_bucket_rows(**kwargs)
        yield from self._generate_draft_rows(**kwargs)

    def _generate_pid_rows(self, **kwargs):
        """Generates rows for a new draft."""
        if self.pid["pid_type"] != "depid":
            # FIXME: temporary fix to test the microseconds conversion
            # should be moved to a mixin or similar on the transform step
            from datetime import datetime

            self.pid["created"] = datetime.fromtimestamp(
                self.pid["created"] / 1_000_000
            )
            self.pid["updated"] = datetime.fromtimestamp(
                self.pid["updated"] / 1_000_000
            )

            # note would raise an exception if it exists
            self.pids_state.add(
                self.pid["pid_value"],  # recid
                {
                    "id": self.pid["id"],
                    "pid_type": self.pid["pid_type"],
                    "status": self.pid["status"],
                    "obj_type": self.pid["object_type"],
                    "created": self.pid["created"],
                },
            )
            yield Operation(OperationType.INSERT, PersistentIdentifier(**self.pid))

    def _generate_bucket_rows(self, **kwargs):
        """Generates rows for a new draft."""
        # FIXME: temporary fix to test the microseconds conversion
        # should be moved to a mixin or similar on the transform step
        from datetime import datetime

        self.bucket["created"] = datetime.fromtimestamp(
            self.bucket["created"] / 1_000_000
        )
        self.bucket["updated"] = datetime.fromtimestamp(
            self.bucket["updated"] / 1_000_000
        )

        yield Operation(OperationType.INSERT, FilesBucket(**self.bucket))

    def _generate_draft_rows(self, **kwargs):
        """Generates rows for a new draft."""
        now = datetime.utcnow().isoformat()

        # some legacy records have different pid value in deposit than record
        # however _deposit.pid.value would contain the correct one
        # if it is not legacy we get it from the current field (json.id)
        recid = self.draft["json"]["id"]
        forked_published = self.records_state.get(recid)

        existing_parent = self.parents_state.get(self.parent["json"]["id"])
        # parent id
        #  a) draft of a published record, parent id = parent id of published
        #  b) new version, parent id = parent id of the previous version
        #  c) draft of a new record, parent id = given by pk func
        # both values should be equal at first, the first is not calculated as pk func
        self.draft["parent_id"] = self.parent["id"]
        if not existing_parent:  # case c
            self.parents_state.add(
                self.parent["json"]["id"],  # recid
                {
                    "id": self.parent["id"],
                    "next_draft_id": self.draft["id"],
                },
            )
            # drafts have a parent on save
            # on the other hand there is no community parent/request
            # FIXME: temporary fix to test the microseconds conversion
            # should be moved to a mixin or similar on the transform step
            self.parent["created"] = datetime.fromtimestamp(
                self.parent["created"] / 1_000_000
            )
            self.parent["updated"] = datetime.fromtimestamp(
                self.parent["updated"] / 1_000_000
            )
            for obj in generate_parent_rows(self.parent):
                # cannot use yield from because we have to add `op`
                yield Operation(OperationType.INSERT, obj)

        else:  # case a and b
            self.parent["id"] = existing_parent["id"]
            self.draft["parent_id"] = existing_parent["id"]  # keep metadata consistent
            if not forked_published:
                # it can only happen once
                assert not existing_parent.get("next_draft_id")
                self.parents_state.update(
                    self.parent["json"]["id"],
                    {"next_draft_id": self.draft["id"]},
                )
            else:
                # state parent  and an existing record must match
                assert self.parent["id"] == forked_published["parent_id"]

        if not forked_published:
            # recid must have been created by a previous action in the same tx group
            draft_pid = self.pids_state.get(self.draft["json"]["id"])
            assert draft_pid

            # update to add object_uuid
            # could avoid this operation but it is clearer on when and why this happens
            yield Operation(
                OperationType.UPDATE,
                PersistentIdentifier(
                    id=draft_pid["id"],  # pk
                    pid_type=draft_pid["pid_type"],  # in drafts are recid
                    pid_value=self.draft["json"]["id"],
                    status=draft_pid["status"],
                    object_type="rec",  # hardcoded since the state has the initial one
                    object_uuid=self.draft["id"],
                    created=draft_pid["created"],
                    updated=now,
                ),
            )

        # FIXME: temporary fix to test the microseconds conversion
        # should be moved to a mixin or similar on the transform step
        self.draft["created"] = datetime.fromtimestamp(
            self.draft["created"] / 1_000_000
        )
        self.draft["updated"] = datetime.fromtimestamp(
            self.draft["updated"] / 1_000_000
        )

        yield Operation(
            OperationType.INSERT,
            RDMDraftMetadata(
                id=forked_published.get("id") or self.draft["id"],
                json=self.draft["json"],
                created=self.draft["created"],
                updated=self.draft["updated"],
                version_id=self.draft["version_id"],
                index=forked_published.get("index") or self.draft["index"],
                bucket_id=self.draft["bucket_id"],
                parent_id=self.parent["id"],
                expires_at=self.draft["expires_at"],
                fork_version_id=forked_published.get("fork_version_id")
                or self.draft["fork_version_id"],
            ),
        )

        # FIXME: this query can be avoided by keeping a consistent view across this method
        # I dont want to refactor yet another thing on this PR.
        existing_parent = self.parents_state.get(self.parent["json"]["id"])

        version_op = OperationType.UPDATE if forked_published else OperationType.INSERT
        yield Operation(
            version_op,
            RDMVersionState(
                latest_index=existing_parent["latest_index"],
                parent_id=existing_parent["id"],
                latest_id=existing_parent["latest_id"],
                next_draft_id=existing_parent["next_draft_id"],
            ),
        )

    def _resolve_references(self, **kwargs):
        """Resolve references e.g communities slug names."""
        # resolve parent communities slug
        parent = self.parent
        communities = parent["json"].get("communities")
        if communities:
            self.resolve_communities(communities)
        self.resolve_draft_pids(self.draft)
