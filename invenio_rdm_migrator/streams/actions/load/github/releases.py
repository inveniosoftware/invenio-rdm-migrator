# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GitHub hooks actions module."""

from dataclasses import dataclass
from typing import Optional

import sqlalchemy as sa

from .....actions import LoadAction, LoadData
from .....load.ids import generate_recid, generate_uuid
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.files import FilesBucket, FilesInstance, FilesObjectVersion
from ....models.github import Release, Repository
from ....models.pids import PersistentIdentifier
from ....models.records import (
    RDMParentMetadata,
    RDMRecordFile,
    RDMRecordMetadata,
    RDMVersionState,
)


@dataclass
class ReleaseData(LoadData):
    """GitHub release action data."""

    gh_release: dict
    gh_repository: Optional[dict] = None


class ReleaseReceiveAction(LoadAction):
    """Receive/Create a GitHub release action."""

    name = "gh-release-receive"
    data_cls = ReleaseData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        assert self.data.gh_repository
        yield Operation(OperationType.UPDATE, Repository, self.data.gh_repository)
        yield Operation(OperationType.INSERT, Release, self.data.gh_release)


class ReleaseUpdateAction(LoadAction):
    """Update a GitHub release action."""

    name = "gh-release-update"
    data_cls = ReleaseData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        yield Operation(OperationType.UPDATE, Release, self.data.gh_release)


@dataclass
class ReleaseProcessData(LoadData):
    """GitHub release action data."""

    record_pid: dict
    record_doi: dict
    record_oai: dict
    file_bucket: dict
    file_object: dict
    file_instance: dict
    file_record: dict
    parent: dict
    record: dict
    gh_release: dict

    parent_pid: Optional[dict] = None
    parent_doi: Optional[dict] = None


class ReleaseProcessAction(LoadAction):
    """Update a GitHub release action."""

    name = "gh-release-process"
    data_cls = ReleaseProcessData
    pks = [
        ("draft", "id", generate_uuid),
        ("parent", "id", generate_uuid),
        # TODO: decide if transform makes the json.pid or not, in drafts we do like that
        # not both parent.json.pid and draft.json.pid come filled in from the
        # transform action to match parent_pid and draft_pid data.
        # there is a TODO (to do it in the load - here -) in rdm-migrator/actions/drafts
        ("record", "json.pid", generate_recid),
        ("parent", "json.pid", generate_recid),
    ]

    def _generate_rows(self, session, **kwargs):
        """Generates rows for a gh repo update."""
        # pids

        # match gen pk
        self.data.record_pid["id"] = self.data.record["json"]["pid"]["pk"]
        yield Operation(
            OperationType.INSERT, PersistentIdentifier, self.data.record_pid
        )
        yield Operation(
            OperationType.INSERT, PersistentIdentifier, self.data.record_doi
        )
        yield Operation(
            OperationType.INSERT, PersistentIdentifier, self.data.record_oai
        )
        if self.data.parent_pid:  # first version
            self.data.parent_pid["id"] = self.data.parent["json"]["pid"]["pk"]
            yield Operation(
                OperationType.INSERT, PersistentIdentifier, self.data.parent_pid
            )
        if self.data.parent_doi:  # first version
            yield Operation(
                OperationType.INSERT, PersistentIdentifier, self.data.parent_doi
            )

        # bucket
        # no need to manage BUCKETS nor FILE_RECORD state
        # since after publishing the respective entries must be deleted from it
        # see drafts actions for clarification
        yield Operation(OperationType.INSERT, FilesBucket, self.data.file_bucket)
        # fi has a ref to fo so has to be inserted before
        yield Operation(OperationType.INSERT, FilesInstance, self.data.file_instance)
        yield Operation(OperationType.INSERT, FilesObjectVersion, self.data.file_object)
        yield Operation(OperationType.INSERT, RDMRecordFile, self.data.file_record)

        # records
        existing_parent_id = session.scalar(
            sa.select(PersistentIdentifier.object_uuid).where(
                PersistentIdentifier.pid_value == self.data.parent["json"]["id"],
                PersistentIdentifier.pid_type == "recid",
            )
        )
        parent_id = existing_parent_id or self.data.parent["id"]

        yield Operation(
            OperationType.DELETE,
            RDMRecordMetadata,
            dict(
                id=self.data.record["id"],
                json=self.data.record["json"],
                created=self.data.record["created"],
                updated=self.data.record["updated"],
                version_id=self.data.record["version_id"],
                index=self.data.record["index"],
                bucket_id=self.data.record["bucket_id"],
                parent_id=parent_id,
                expires_at=self.data.record["expires_at"],
                fork_version_id=self.data.record["fork_version_id"],
            ),
        )

        # parent and state
        if not existing_parent_id:
            yield Operation(
                OperationType.INSERT,
                RDMParentMetadata,
                dict(
                    id=parent_id,
                    json=self.data.parent["json"],
                    created=self.data.parent["created"],
                    updated=self.data.parent["updated"],
                    version_id=self.data.parent["version_id"],
                ),
            )

        # versioning
        versioning_op = (
            OperationType.UPDATE if existing_parent_id else OperationType.INSERT
        )
        yield Operation(
            versioning_op,
            RDMVersionState,
            dict(
                parent_id=self.data.parent["id"],
                latest_id=self.data.record["id"],
                latest_index=self.data.record["index"],
                next_draft_id=None,
            ),
        )
