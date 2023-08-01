# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration drafts row load module."""

from dataclasses import dataclass
from datetime import datetime
from functools import partial

from ...actions import LoadAction, LoadData
from ...load.ids import generate_pk, generate_recid, generate_uuid
from ...load.postgresql.transactions.operations import Operation, OperationType
from ...state import STATE
from ..models.files import FilesBucket
from ..models.pids import PersistentIdentifier
from ..models.records import RDMDraftMetadata, RDMVersionState
from ..records.table_generators.parents import generate_parent_rows
from ..records.table_generators.references import (
    CommunitiesReferencesMixin,
    PIDsReferencesMixin,
)


@dataclass
class RDMDraftCreateData(LoadData):
    """Draft create action data."""

    # NOTE: we could go with some common ``typing.TypedDict`` definitions to help more
    pid: dict
    bucket: dict
    draft: dict
    parent: dict


class DraftCreateAction(LoadAction, CommunitiesReferencesMixin, PIDsReferencesMixin):
    """RDM draft creation."""

    name = "create-draft"
    data_cls = RDMDraftCreateData

    pks = [
        ("pid", "id", generate_pk),
        ("draft", "id", generate_uuid),
        ("parent", "id", generate_uuid),
        ("parent", "json.pid", generate_recid),
        ("draft", "json.pid", partial(generate_recid, status="N")),
    ]

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        yield from self._generate_pid_rows(**kwargs)
        yield from self._generate_bucket_rows(**kwargs)
        yield from self._generate_draft_rows(**kwargs)

    def _generate_pid_rows(self, **kwargs):
        """Generates rows for a new draft."""
        pid = self.data.pid
        if pid["pid_type"] != "depid":
            # https://github.com/inveniosoftware/invenio-rdm-migrator/issues/123
            from datetime import datetime

            pid["created"] = datetime.fromtimestamp(pid["created"] / 1_000_000)
            pid["updated"] = datetime.fromtimestamp(pid["updated"] / 1_000_000)

            # note would raise an exception if it exists
            STATE.PIDS.add(
                pid["pid_value"],  # recid
                {
                    "id": pid["id"],
                    "pid_type": pid["pid_type"],
                    "status": pid["status"],
                    "obj_type": pid["object_type"],
                    "created": pid["created"],
                },
            )
            yield Operation(OperationType.INSERT, PersistentIdentifier(**pid))

    def _generate_bucket_rows(self, **kwargs):
        """Generates rows for a new draft."""
        # https://github.com/inveniosoftware/invenio-rdm-migrator/issues/123

        bucket = self.data.bucket
        bucket["created"] = datetime.fromtimestamp(bucket["created"] / 1_000_000)
        bucket["updated"] = datetime.fromtimestamp(bucket["updated"] / 1_000_000)

        yield Operation(OperationType.INSERT, FilesBucket(**bucket))

    def _generate_draft_rows(self, **kwargs):
        """Generates rows for a new draft."""
        now = datetime.utcnow().isoformat()

        draft = self.data.draft
        parent = self.data.parent

        # some legacy records have different pid value in deposit than record
        # however _deposit.pid.value would contain the correct one
        # if it is not legacy we get it from the current field (json.id)
        recid = draft["json"]["id"]
        forked_published = STATE.RECORDS.get(recid)

        existing_parent = STATE.PARENTS.get(parent["json"]["id"])
        # parent id
        #  a) draft of a published record, parent id = parent id of published
        #  b) new version, parent id = parent id of the previous version
        #  c) draft of a new record, parent id = given by pk func
        # both values should be equal at first, the first is not calculated as pk func
        draft["parent_id"] = parent["id"]
        if not existing_parent:  # case c
            STATE.PARENTS.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "next_draft_id": draft["id"],
                },
            )
            # drafts have a parent on save
            # on the other hand there is no community parent/request
            # https://github.com/inveniosoftware/invenio-rdm-migrator/issues/123
            parent["created"] = datetime.fromtimestamp(parent["created"] / 1_000_000)
            parent["updated"] = datetime.fromtimestamp(parent["updated"] / 1_000_000)
            for obj in generate_parent_rows(parent):
                # cannot use yield from because we have to add `op`
                yield Operation(OperationType.INSERT, obj)

        else:  # case a and b
            parent["id"] = existing_parent["id"]
            draft["parent_id"] = existing_parent["id"]  # keep metadata consistent
            if not forked_published:
                # it can only happen once
                assert not existing_parent.get("next_draft_id")
                STATE.PARENTS.update(
                    parent["json"]["id"],
                    {"next_draft_id": draft["id"]},
                )
            else:
                # state parent  and an existing record must match
                assert parent["id"] == forked_published["parent_id"]

        if not forked_published:
            # recid must have been created by a previous action in the same tx group
            draft_pid = STATE.PIDS.get(draft["json"]["id"])
            assert draft_pid

            # update to add object_uuid
            # could avoid this operation but it is clearer on when and why this happens
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

        # https://github.com/inveniosoftware/invenio-rdm-migrator/issues/123
        draft["created"] = datetime.fromtimestamp(draft["created"] / 1_000_000)
        draft["updated"] = datetime.fromtimestamp(draft["updated"] / 1_000_000)

        yield Operation(
            OperationType.INSERT,
            RDMDraftMetadata(
                id=forked_published.get("id") or draft["id"],
                json=draft["json"],
                created=draft["created"],
                updated=draft["updated"],
                version_id=draft["version_id"],
                index=forked_published.get("index") or draft["index"],
                bucket_id=draft["bucket_id"],
                parent_id=parent["id"],
                expires_at=draft["expires_at"],
                fork_version_id=forked_published.get("fork_version_id")
                or draft["fork_version_id"],
            ),
        )

        # this query can be avoided by keeping a consistent view across this method
        existing_parent = STATE.PARENTS.get(parent["json"]["id"])

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
        parent = self.data.parent
        communities = parent["json"].get("communities")
        if communities:
            self.resolve_communities(communities)
        self.resolve_draft_pids(self.data.draft)
