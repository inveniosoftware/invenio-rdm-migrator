# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration drafts row load module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

import sqlalchemy as sa

from ....actions import LoadAction, LoadData
from ....load.postgresql.transactions.operations import Operation, OperationType
from ...models.communities import Community, CommunityMember
from ...models.files import FilesBucket, FilesObjectVersion
from ...models.pids import PersistentIdentifier
from ...models.records import (
    RDMDraftFile,
    RDMDraftMetadata,
    RDMParentMetadata,
    RDMRecordFile,
    RDMRecordMetadata,
    RDMVersionState,
)


def _get_community_id(session, slug):
    return session.execute(
        sa.select(Community.id).where(Community.slug == slug)
    ).one_or_none()


def _set_permission_flags(session, parent, draft_or_record):
    comm_ids = set(parent.get("communities", {}).get("ids", []))
    if comm_ids:
        permission_flags = {}
        owner_id = parent["json"].get("access", {}).get("owned_by", {}).get("user")
        owner_comm_ids = session.scalars(
            sa.select(Community.id)
            .join(CommunityMember, Community.id == CommunityMember.community_id)
            .where(
                CommunityMember.role == "owner",
                CommunityMember.user_id == owner_id,
            )
        ).all()
        has_only_managed_communities = comm_ids <= set(owner_comm_ids)
        if not has_only_managed_communities:
            permission_flags["can_community_manage_record"] = False
            draft_files_access = draft_or_record["json"].get("access", {}).get("files")
            if draft_files_access != "public":
                permission_flags["can_community_read_files"] = False
        if permission_flags:
            parent["json"]["permission_flags"] = permission_flags


def resolve_communities(session, communities):
    default_slug = communities.get("default")
    if default_slug:
        community_id = _get_community_id(session, default_slug)
        if community_id:
            communities["default"] = community_id
        else:
            communities.pop("default", None)
            communities["ids"].remove(default_slug)

    communities_slugs = communities.get("ids", [])
    _ids = []
    for slug in communities_slugs:
        community_id = _get_community_id(session, slug)
        if community_id:
            _ids.append(community_id)

    communities["ids"] = _ids


def format_pid_ref(pid):
    return {
        "pk": pid.id,
        "obj_type": pid.object_type,
        "pid_type": pid.pid_type,
        "status": pid.status,
    }


def get_published_record(session, recid) -> Optional[RDMRecordMetadata]:
    return session.scalars(
        sa.select(RDMRecordMetadata)
        .join(
            PersistentIdentifier,
            RDMRecordMetadata.id == PersistentIdentifier.object_uuid,
        )
        .where(
            PersistentIdentifier.pid_type == "recid",
            PersistentIdentifier.object_type == "rec",
            PersistentIdentifier.pid_value == recid,
        )
    ).one_or_none()


def get_pid(session, pid_type, pid_value) -> Optional[PersistentIdentifier]:
    return session.scalars(
        sa.select(PersistentIdentifier).where(
            PersistentIdentifier.pid_type == pid_type,
            PersistentIdentifier.pid_value == pid_value,
        )
    ).one_or_none()


def delete_ov(session, bucket_id, key):
    obj = session.scalar(
        sa.select(FilesObjectVersion).where(
            FilesObjectVersion.bucket_id == bucket_id,
            FilesObjectVersion.key == key,
            FilesObjectVersion.is_head.is_(True),
            FilesObjectVersion.file_id.isnot(None),
        )
    )
    if obj:
        yield Operation(
            OperationType.UPDATE,
            FilesObjectVersion,
            {"version_id": obj.version_id, "is_head": False},
        )
        yield Operation(
            OperationType.INSERT,
            FilesObjectVersion,
            {
                "version_id": uuid4(),
                "is_head": True,
            },
        )


def copy_ov(session, src, bucket_id, version_id=None, created=None, updated=None):
    latest_obj = session.scalar(
        sa.select(FilesObjectVersion).where(
            FilesObjectVersion.bucket_id == bucket_id,
            FilesObjectVersion.key == src.key,
            FilesObjectVersion.is_head.is_(True),
        )
    )
    if latest_obj is not None:
        yield Operation(
            OperationType.UPDATE,
            FilesObjectVersion,
            {"version_id": latest_obj.version_id, "is_head": False},
        )

    yield Operation(
        OperationType.INSERT,
        FilesObjectVersion,
        {
            "version_id": version_id or uuid4(),
            "is_head": True,
            "bucket_id": bucket_id,
            "key": src.key,
            "file_id": src.file_id,
            "created": created or datetime.utcnow(),
            "updated": updated or datetime.utcnow(),
        },
    )


def synchronize_files(session, draft, draft_bucket, record, record_bucket):
    draft_ovs = session.scalars(
        sa.select(FilesObjectVersion)
        .join(
            FilesObjectVersion,
            RDMDraftFile.object_version_id == FilesObjectVersion.version_id,
        )
        .where(
            RDMDraftFile.record_id == draft["id"],
            FilesObjectVersion.is_head.is_(True),
        )
    ).all()

    record_ovs = session.scalars(
        sa.select(FilesObjectVersion)
        .join(
            FilesObjectVersion,
            RDMRecordFile.object_version_id == FilesObjectVersion.version_id,
        )
        .where(
            RDMRecordFile.record_id == record["id"],
            FilesObjectVersion.is_head.is_(True),
        )
    ).all()

    changed_ovs = []
    draft_dict_ovs = {}
    for ov in draft_ovs:
        if ov.key not in draft_dict_ovs:
            draft_dict_ovs[ov.key] = ov

    record_dict_ovs = {}
    for ov in record_ovs:
        if ov.key not in record_dict_ovs:
            record_dict_ovs[ov.key] = ov

    for key, ov in draft_dict_ovs.items():
        key_in_dest = key in record_dict_ovs
        if ov.file_id is None:
            if key_in_dest and record_dict_ovs[key].file_id is not None:
                yield from delete_ov(session, record_bucket["id"], key)
                changed_ovs.append(("delete", key))
        else:
            if not key_in_dest:
                new_ov_id = None
                for op in copy_ov(session, ov, record_bucket["id"]):
                    new_ov_id = op.data["version_id"]
                    yield op
                if new_ov_id:
                    changed_ovs.append(("add", new_ov_id))
            else:
                record_ov = record_dict_ovs[key]
                file_in_record_differs = ov.file_id != record_ov.file_id
                ov_deleted_in_dest = record_ov.file_id is None
                if file_in_record_differs or ov_deleted_in_dest:
                    new_ov_id = None
                    for op in copy_ov(session, ov, record_bucket["id"]):
                        new_ov_id = op.data["version_id"]
                        yield op
                    if new_ov_id:
                        if ov_deleted_in_dest:
                            changed_ovs.append(("add", new_ov_id))
                        else:
                            changed_ovs.append(("update", new_ov_id))

    for key, ov in record_dict_ovs.items():
        if key not in draft_dict_ovs:
            yield from delete_ov(session, record_bucket["id"], key)
            changed_ovs.append(("delete", key))
    # TODO: Process `changed_ovs` to apply changes to RDMFileRecord


def resolve_draft_pids(session, draft, parent=None):
    """Enforce record's pids to draft."""
    if not draft:
        return

    pid = draft["json"]["id"]
    forked_published = get_published_record(session, pid)
    if forked_published:
        pids = draft["json"]["pids"]
        has_draft_external_doi = pids.get("doi", {}).get("provider") == "external"
        if has_draft_external_doi:
            # keep the draft external value as it might be there for
            # updating the existing value. Update the draft only with `oai`
            pids["oai"] = forked_published.json["pids"]["oai"]
        else:
            # enfore published record pids to draft
            draft["json"]["pids"] = forked_published.json["pids"]

        if parent:
            parent_model = session.scalars(
                sa.select(RDMParentMetadata).where(
                    RDMParentMetadata.id == forked_published.parent_id
                )
            ).one()
            parent["json"]["pids"] = parent_model.json["pids"]


@dataclass
class RDMDraftCreateData(LoadData):
    """Draft create action data."""

    pid: dict
    draft: dict
    draft_bucket: dict
    parent_pid: dict
    parent: dict


class DraftCreateAction(LoadAction):
    """RDM draft creation."""

    name = "create-draft"
    data_cls = RDMDraftCreateData
    data: RDMDraftCreateData

    def _generate_rows(self, session, **kwargs):
        """Generates rows for a new draft."""
        draft = self.data.draft
        draft["id"] = str(uuid4())
        parent = self.data.parent
        parent.setdefault("id", str(uuid4()))
        pid = self.data.pid

        published_record = get_published_record(session, draft["json"]["id"])
        version_state = session.scalars(
            sa.select(RDMVersionState).where(RDMVersionState.parent_id == parent["id"])
        ).one_or_none()

        is_first_publish_draft = not published_record and not version_state
        is_new_version_draft = version_state and not published_record

        if is_first_publish_draft or is_new_version_draft:
            # Recid PID
            pid.update(
                {
                    "pid_type": "recid",
                    "object_type": "rec",
                    "object_uuid": draft["id"],
                    "status": "R",
                }
            )
            yield Operation(OperationType.INSERT, PersistentIdentifier, pid)
            pid_model = get_pid(session, "recid", pid["pid_value"])
            assert pid_model
            self.data.draft["json"]["pid"] = format_pid_ref(pid_model)
            # Bucket
            yield Operation(OperationType.INSERT, FilesBucket, self.data.draft_bucket)
        else:
            raise Exception("Draft PID creation in invalid state.")

        # Parent
        #  A) draft of a published record, parent id = parent id of published
        #  B) new version, parent id = parent id of the previous version
        #  C) draft of a new record, parent id = given by pk func
        if is_first_publish_draft:
            parent_pid = self.data.parent_pid
            parent_pid.update(
                {
                    "pid_type": "recid",
                    "object_type": "rec",
                    "object_uuid": parent["id"],
                    "status": "R",
                }
            )
            yield Operation(OperationType.INSERT, PersistentIdentifier, parent_pid)
            parent_pid_model = get_pid(session, "recid", parent_pid["pid_value"])
            assert parent_pid_model
            self.data.parent["json"]["pid"] = format_pid_ref(parent_pid_model)
            yield Operation(
                OperationType.INSERT,
                RDMParentMetadata,
                dict(
                    id=parent["id"],
                    json=parent["json"],
                    created=parent["created"],
                    updated=parent["updated"],
                    version_id=parent["version_id"],
                ),
            )
        else:
            raise Exception("Draft parent creation in invalid state.")
        draft["parent_id"] = parent["id"]

        if is_first_publish_draft or is_new_version_draft:
            if is_first_publish_draft:
                draft_index = 1
            else:
                assert version_state
                draft_index = version_state.latest_index + 1
            yield Operation(
                OperationType.INSERT,
                RDMDraftMetadata,
                dict(
                    id=draft["id"],
                    json=draft["json"],
                    created=draft["created"],
                    updated=draft["updated"],
                    version_id=draft["version_id"],
                    index=draft_index,
                    bucket_id=draft["bucket_id"],
                    parent_id=parent["id"],
                    expires_at=draft["expires_at"],
                    fork_version_id=None,
                ),
            )

        if is_first_publish_draft:
            yield Operation(
                OperationType.INSERT,
                RDMVersionState,
                dict(
                    latest_index=None,
                    parent_id=parent["id"],
                    latest_id=None,
                    next_draft_id=draft["id"],
                ),
            )
        elif is_new_version_draft:
            yield Operation(
                OperationType.UPDATE,
                RDMVersionState,
                dict(
                    parent_id=parent["id"],
                    next_draft_id=draft["id"],
                ),
            )

    def _resolve_references(self, session, **kwargs):
        """Resolve references e.g communities slug names."""
        parent = self.data.parent
        parent_pid = get_pid(session, "recid", parent["json"]["id"])
        if parent_pid:
            parent["id"] = str(parent_pid.object_uuid)

        # resolve parent communities slug
        communities = parent["json"].get("communities")
        if communities:
            resolve_communities(session, communities)
        resolve_draft_pids(session, self.data.draft)
        _set_permission_flags(session, parent, self.data.draft)


@dataclass
class RDMDraftEditData(LoadData):
    """Draft edit action data."""

    draft: dict
    parent: dict
    bucket: Optional[dict]


class DraftEditAction(LoadAction):
    """RDM draft edit/update."""

    name = "edit-draft"
    data_cls = RDMDraftEditData
    data: RDMDraftEditData

    def _generate_rows(self, session, **kwargs):
        """Generates rows for a new draft."""
        draft = self.data.draft

        fork_version_id = session.scalar(
            sa.select(RDMRecordMetadata.version_id).where(
                RDMDraftMetadata.id == draft["id"]
            )
        )
        yield Operation(
            OperationType.UPDATE,
            RDMDraftMetadata,
            {
                "id": draft["id"],
                "json": draft["json"],
                "updated": draft["updated"],
                "fork_version_id": fork_version_id,
                RDMDraftMetadata.version_id: RDMDraftMetadata.version_id + 1,
            },
        )
        if self.data.bucket:
            yield Operation(
                OperationType.UPDATE,
                FilesBucket,
                {
                    "id": self.data.bucket["id"],
                    "size": self.data.bucket["size"],
                    "locked": self.data.bucket["locked"],
                    "updated": self.data.bucket["updated"],
                },
            )

    def _resolve_references(self, session, **kwargs):
        """Resolve references e.g communities slug names."""
        draft = self.data.draft
        draft_pid = get_pid(session, "recid", draft["json"]["id"])
        assert draft_pid
        draft["id"] = str(draft_pid.object_uuid)
        draft["index"] = session.scalar(
            sa.select(RDMDraftMetadata.index).where(RDMDraftMetadata.id == draft["id"])
        )
        draft["json"]["pid"] = format_pid_ref(draft_pid)

        parent = self.data.parent
        parent_pid = get_pid(session, "recid", parent["json"]["id"])
        assert parent_pid
        parent["id"] = str(parent_pid.object_uuid)
        parent["json"]["pid"] = format_pid_ref(parent_pid)

        # resolve parent communities slug
        communities = parent.get("json", {}).get("communities")
        if communities:
            resolve_communities(session, communities)

        resolve_draft_pids(session, self.data.draft, parent=parent)
        _set_permission_flags(session, parent, self.data.draft)


@dataclass
class RDMDraftPublishNewData(LoadData):
    """Draft new publish action data."""

    # Files
    draft_bucket: dict
    record_bucket: dict
    record_object_versions: list[dict]

    # Records
    parent: dict
    draft: dict
    record: dict

    # PIDs
    pid: dict
    oai_pid: dict
    doi: dict
    parent_pid: Optional[dict] = None
    parent_doi: Optional[dict] = None

    # Communities?


class DraftPublishNewAction(LoadAction):
    """RDM new publish action."""

    name = "publish-new-draft"
    data_cls = RDMDraftPublishNewData
    data: RDMDraftPublishNewData

    def _generate_rows(self, session, **kwargs):
        """Generates rows for a new draft."""
        is_first_publish = self.data.parent_pid is not None
        is_local_doi = self.data.parent_doi is not None

        draft = self.data.draft
        record = self.data.record
        parent = self.data.parent
        #
        # Files rows
        #
        draft_bucket = self.data.draft_bucket
        record_bucket = self.data.record_bucket

        record_bucket["locked"] = True
        yield Operation(OperationType.INSERT, FilesBucket, record_bucket)
        yield Operation(
            OperationType.UPDATE,
            FilesBucket,
            {
                "id": draft_bucket["id"],
                "updated": draft_bucket["updated"],
                "locked": True,
            },
        )

        record_object_versions = self.data.record_object_versions
        for record_ov in record_object_versions:
            yield Operation(OperationType.INSERT, FilesObjectVersion, record_ov)
            yield Operation(
                OperationType.INSERT,
                RDMRecordFile,
                {
                    "id": str(uuid4()),
                    "created": record_ov["created"],
                    "updated": record_ov["updated"],
                    "json": {},
                    "version_id": 1,
                    "key": record_ov["key"],
                    "record_id": record["id"],
                    "object_version_id": record_ov["version_id"],
                },
            )

        #
        # PID rows
        #
        pid = self.data.pid
        pid_model = get_pid(session, "recid", pid["pid_value"])
        assert pid_model
        yield Operation(
            OperationType.UPDATE,
            PersistentIdentifier,
            {
                "id": pid_model.id,
                "status": "R",
                "updated": pid["updated"],
            },
        )

        doi = self.data.doi
        doi["object_uuid"] = record["id"]
        doi["status"] = "R"
        yield Operation(OperationType.INSERT, PersistentIdentifier, doi)

        oai_pid = self.data.oai_pid
        oai_pid["status"] = "R"
        oai_pid["object_uuid"] = record["id"]
        yield Operation(OperationType.INSERT, PersistentIdentifier, oai_pid)

        if is_first_publish:
            parent_pid = self.data.parent_pid
            assert parent_pid
            parent_pid_model = get_pid(session, "recid", parent_pid["pid_value"])
            assert parent_pid_model
            yield Operation(
                OperationType.UPDATE,
                PersistentIdentifier,
                {
                    "id": parent_pid_model.id,
                    "status": "R",
                    "updated": parent_pid["updated"],
                },
            )
            if is_local_doi:
                parent_doi = self.data.parent_doi
                assert parent_doi
                parent_doi["object_uuid"] = parent["id"]
                parent_doi["status"] = "R"
                yield Operation(OperationType.INSERT, PersistentIdentifier, parent_doi)

        #
        # Draft rows
        #
        # Soft-delete draft
        yield Operation(
            OperationType.UPDATE,
            RDMDraftMetadata,
            {
                "id": draft["id"],
                "json": None,
                "updated": draft["updated"],
                RDMDraftMetadata.version_id: RDMDraftMetadata.version_id + 1,
                "fork_version_id": None,
            },
        )

        # Create record
        yield Operation(
            OperationType.INSERT,
            RDMRecordMetadata,
            dict(
                id=record["id"],
                json=record["json"],
                created=record["updated"],
                updated=record["updated"],
                version_id=1,
                index=draft["index"],  # take from drat
                bucket_id=record_bucket["id"],
                parent_id=parent["id"],
                deletion_status="P",
            ),
        )
        # Update parent
        yield Operation(
            OperationType.UPDATE,
            RDMParentMetadata,
            {
                "id": parent["id"],
                "json": parent["json"],
                "updated": parent["updated"],
                RDMParentMetadata.version_id: RDMParentMetadata.version_id + 1,
            },
        )
        yield Operation(
            OperationType.UPDATE,
            RDMVersionState,
            dict(
                parent_id=parent["id"],
                latest_id=record["id"],
                latest_index=draft["index"],
                next_draft_id=None,
            ),
        )

    def _resolve_references(self, session, **kwargs):
        """Resolve references e.g communities slug names."""
        draft = self.data.draft
        draft_pid = get_pid(session, "recid", draft["json"]["id"])
        assert draft_pid
        draft["id"] = str(draft_pid.object_uuid)
        draft["index"] = session.scalar(
            sa.select(RDMDraftMetadata.index).where(RDMDraftMetadata.id == draft["id"])
        )
        draft["json"]["pid"] = format_pid_ref(draft_pid)
        # In RDM drafts and records share their PK
        self.data.record["id"] = draft["id"]
        self.data.record["json"]["pid"] = draft["json"]["pid"]

        parent = self.data.parent
        parent_pid = get_pid(session, "recid", parent["json"]["id"])
        assert parent_pid
        parent["id"] = str(parent_pid.object_uuid)
        parent["json"]["pid"] = format_pid_ref(parent_pid)

        # resolve parent communities slug
        communities = parent["json"].get("communities")
        if communities:
            resolve_communities(session, communities)
        resolve_draft_pids(session, self.data.draft, parent=parent)
        _set_permission_flags(session, parent, self.data.draft)


@dataclass
class RDMDraftPublishEditData(LoadData):
    """Draft edit publish action data."""

    # Files
    draft_bucket: Optional[dict]
    record_bucket: Optional[dict]
    record_object_versions: Optional[dict]

    # Records
    parent: dict
    draft: dict
    record: dict

    # PIDs
    old_external_doi: Optional[dict]
    new_external_doi: Optional[dict]

    # Communities?


class DraftPublishEditAction(LoadAction):
    """RDM edit publish creation."""

    name = "publish-edit-draft"
    data_cls = RDMDraftPublishEditData
    data: RDMDraftPublishEditData

    def _generate_rows(self, session, **kwargs):
        """Generates rows for a new draft."""
        is_external_doi = self.data.old_external_doi or self.data.old_external_doi

        draft = self.data.draft
        record = self.data.record
        parent = self.data.parent

        #
        # Files rows
        #
        if is_external_doi and self.data.record_object_versions:
            # TODO: Synchronize files
            yield from synchronize_files(
                session,
                draft,
                self.data.draft_bucket,
                record,
                self.data.record_bucket,
            )
        #
        # PID rows
        #
        external_doi_changed = self.data.old_external_doi and self.data.new_external_doi
        if external_doi_changed:
            old_doi = self.data.old_external_doi
            assert old_doi
            old_doi_model = get_pid(session, "doi", old_doi["pid_value"])
            assert old_doi_model
            yield Operation(
                OperationType.DELETE, PersistentIdentifier, {"id": old_doi_model.id}
            )
            new_doi = self.data.new_external_doi
            assert new_doi
            new_doi["object_uuid"] = record["id"]
            yield Operation(OperationType.INSERT, PersistentIdentifier, new_doi)

        #
        # Draft rows
        #
        # Soft-delete draft
        yield Operation(
            OperationType.UPDATE,
            RDMDraftMetadata,
            dict(
                id=draft["id"],
                json=None,
                updated=draft["updated"],
                version_id=draft["version_id"],
                fork_version_id=None,
            ),
        )

        # Create record
        yield Operation(
            OperationType.UPDATE,
            RDMRecordMetadata,
            {
                "id": record["id"],
                "json": record["json"],
                "updated": record["updated"],
                RDMRecordMetadata.version_id: RDMRecordMetadata.version_id + 1,
            },
        )

        # Update parent
        yield Operation(
            OperationType.UPDATE,
            RDMParentMetadata,
            {
                "id": parent["id"],
                "json": parent["json"],
                RDMParentMetadata.version_id: RDMParentMetadata.version_id + 1,
                "updated": parent["updated"],
            },
        )

    def _resolve_references(self, session, **kwargs):
        """Resolve references e.g communities slug names."""
        draft = self.data.draft
        draft_pid = get_pid(session, "recid", draft["json"]["id"])
        assert draft_pid
        draft["id"] = str(draft_pid.object_uuid)
        draft["json"]["pid"] = format_pid_ref(draft_pid)
        self.data.record["id"] = draft["id"]
        self.data.record["id"] = draft["id"]
        self.data.record["json"]["pid"] = draft["json"]["pid"]

        parent = self.data.parent
        parent_pid = get_pid(session, "recid", parent["json"]["id"])
        assert parent_pid
        parent["id"] = str(parent_pid.object_uuid)
        parent["json"]["pid"] = format_pid_ref(parent_pid)

        # resolve parent communities slug
        communities = parent["json"].get("communities")
        if communities:
            resolve_communities(session, communities)
        resolve_draft_pids(session, self.data.draft, parent=parent)
        _set_permission_flags(session, parent, self.data.draft)
