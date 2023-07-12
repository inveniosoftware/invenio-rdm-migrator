# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration drafts row load module."""


from datetime import datetime

from ...load.ids import generate_recid, generate_uuid
from ...load.postgresql.transactions.generators import RowGenerator
from ...load.postgresql.transactions.operations import Operation, OperationType
from ..models.pids import PersistentIdentifier
from ..models.records import RDMDraftMetadata, RDMVersionState
from ..records.table_generators.parents import generate_parent_rows  # FIXME: move
from ..records.table_generators.references import (
    CommunitiesReferencesMixin,
    PIDsReferencesMixin,
)


class RDMDraftTxGenerator(
    RowGenerator, CommunitiesReferencesMixin, PIDsReferencesMixin
):
    """RDM Record and related tables load."""

    def __init__(self, parents_state, records_state, communities_state, pids_state):
        """Constructor."""
        super().__init__(
            pks=[
                ("draft.id", generate_uuid),
                ("parent.id", generate_uuid),
                ("parent.json.pid", generate_recid),
                ("draft.parent_id", lambda d: d["parent"]["id"]),
            ],
        )
        self.parents_state = parents_state
        self.records_state = records_state
        self.communities_state = communities_state
        self.pids_state = pids_state

    # FIXME: not generic enough
    # all memory tg enforce op, in the long run this is not re-usable
    def _generate_rows(self, data, op, **kwargs):
        """Generates rows for a draft.

        This TG will only emit parent record (and pid) if needed and draft metadata.
        It will not emit rows for pids or files, those are treated by other action tg.
        """
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        draft = data.get("draft")
        if not draft:
            return

        # some legacy records have different pid value in deposit than record
        # however _deposit.pid.value would contain the correct one
        # if it is not legacy we get it from the current field (json.id)
        recid = draft["json"]["id"]
        forked_published = self.records_state.get(recid)

        state_parent = self.parents_state.get(parent["json"]["id"])
        if not state_parent:
            self.parents_state.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "next_draft_id": draft["id"],
                },
            )
            # drafts have a parent on save
            # on the other hand there is no community parent/request
            # FIXME: temporary fix to test the microseconds conversion
            # should be moved to a mixin or similar on the transform step
            parent["created"] = datetime.fromtimestamp(parent["created"] / 1_000_000)
            parent["updated"] = datetime.fromtimestamp(parent["updated"] / 1_000_000)
            for obj in generate_parent_rows(parent):
                # cannot use yield from because we have to add `op`
                yield Operation(op, obj)

        # if there is a parent (else) but there is no record it means that it is a
        # draft of a new version
        elif not forked_published:
            assert not state_parent.get("next_draft_id")  # it can only happen once
            self.parents_state.update(
                parent["json"]["id"],
                {
                    "next_draft_id": draft["id"],
                },
            )

        # if its a draft of a published record, its parent should be parent id
        # if its a new version, its parent should be the one of the previous version
        # otherwise is a new parent (new record, new draft...)
        parent_id = state_parent["id"] if state_parent else draft["parent_id"]
        if forked_published:
            parent_id = forked_published["parent_id"]
        else:
            # recid
            # must have been created by a previous action in the same transaction group
            draft_pid = self.pids_state.get(draft["json"]["id"])
            assert draft_pid

            # update to add object_uuid
            yield Operation(
                OperationType.UPDATE,
                PersistentIdentifier(
                    id=draft_pid["id"],  # pk
                    pid_type=draft_pid["pid_type"],  # in drafts are recid
                    pid_value=draft["json"]["id"],
                    status=draft_pid["status"],
                    object_type="rec",  # hardcoded since the state has the initial one
                    object_uuid=draft["id"],
                    created=draft_pid["created"],
                    updated=now,
                ),
            )

        # FIXME: temporary fix to test the microseconds conversion
        # should be moved to a mixin or similar on the transform step
        draft["created"] = datetime.fromtimestamp(draft["created"] / 1_000_000)
        draft["updated"] = datetime.fromtimestamp(draft["updated"] / 1_000_000)

        yield Operation(
            op,
            RDMDraftMetadata(
                id=forked_published.get("id") or draft["id"],
                json=draft["json"],
                created=draft["created"],
                updated=draft["updated"],
                version_id=draft["version_id"],
                index=forked_published.get("index") or draft["index"],
                bucket_id=draft["bucket_id"],  # TODO: check on stat that it exists
                parent_id=parent_id,
                expires_at=draft["expires_at"],
                fork_version_id=forked_published.get("fork_version_id")
                or draft["fork_version_id"],
            ),
        )

        # FIXME: this query can be avoided by keeping a consistent view across this method
        # I dont want to refactor yet another thing on this PR.
        state_parent = self.parents_state.get(parent["json"]["id"])

        version_op = OperationType.UPDATE if forked_published else op
        yield Operation(
            version_op,
            RDMVersionState(
                latest_index=state_parent["latest_index"],
                parent_id=state_parent["id"],
                latest_id=state_parent["latest_id"],
                next_draft_id=state_parent["next_draft_id"],
            ),
        )

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""
        # resolve parent communities slug
        parent = data["parent"]
        communities = parent["json"].get("communities")
        if communities:
            self.resolve_communities(communities)
        self.resolve_draft_pids(data.get("draft"))
