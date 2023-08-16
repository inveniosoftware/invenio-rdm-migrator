# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities actions module."""

from dataclasses import dataclass
from typing import Optional

from ....actions import LoadAction, LoadData
from ....load.ids import generate_pk_for, generate_uuid
from ....load.postgresql.transactions.operations import Operation, OperationType
from ....state import STATE
from ...models.communities import Community, CommunityFile, CommunityMember
from ...models.files import FilesBucket, FilesInstance, FilesObjectVersion
from ...models.oai import OAISet


@dataclass
class CommunityData(LoadData):
    """Community action data."""

    community: dict
    owner: dict
    oai_set: dict
    bucket: dict

    community_file: Optional[dict] = None
    file_instance: Optional[dict] = None
    object_version: Optional[dict] = None


class CommunityCreateAction(LoadAction):
    """Create a community."""

    pks = [
        ("community", "id", generate_uuid),
        ("owner", "id", generate_uuid),
        ("oai_set", "id", generate_pk_for(OAISet)),
        ("bucket", "id", generate_uuid),
        ("community_file", "id", generate_uuid),
    ]

    name = "community-create"
    data_cls = CommunityData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new community."""
        community_id = self.data.community["id"]
        slug = self.data.community["slug"]
        community_file_id = None
        logo_object_version_id = None

        # Fill-in the community bucket
        bucket_id = self.data.bucket["id"]
        self.data.community["bucket_id"] = bucket_id

        yield Operation(OperationType.INSERT, FilesBucket, self.data.bucket)
        yield Operation(OperationType.INSERT, Community, self.data.community)

        oai_set_id = self.data.oai_set["id"]
        self.data.oai_set["search_pattern"] = f"parent.communities.ids:{community_id}"
        self.data.oai_set["system_created"] = True
        yield Operation(OperationType.INSERT, OAISet, self.data.oai_set)

        # Generate owner member
        self.data.owner["community_id"] = community_id
        yield Operation(OperationType.INSERT, CommunityMember, self.data.owner)

        # Not every community has a logo
        if self.data.community_file:
            yield Operation(
                OperationType.INSERT,
                FilesInstance,
                self.data.file_instance,
            )

            object_version = self.data.object_version
            logo_object_version_id = object_version["version_id"]
            object_version["bucket_id"] = bucket_id
            yield Operation(OperationType.INSERT, FilesObjectVersion, object_version)

            community_file = self.data.community_file
            community_file_id = community_file["id"]
            community_file["record_id"] = community_id
            community_file["object_version_id"] = logo_object_version_id
            yield Operation(OperationType.INSERT, CommunityFile, community_file)

        # Add to state
        STATE.COMMUNITIES.add(
            slug,
            {
                "id": community_id,
                "bucket_id": bucket_id,
                "oai_set_id": oai_set_id,
                "community_file_id": community_file_id,
                "logo_object_version_id": logo_object_version_id,
            },
        )


@dataclass
class CommunityUpdateData(LoadData):
    """Community action data."""

    community: dict

    community_file: Optional[dict] = None
    file_instance: Optional[dict] = None
    object_version: Optional[dict] = None

    # Filled-in by the action
    old_object_version_id: Optional[str] = None


class CommunityUpdateAction(LoadAction):
    """Update a community."""

    name = "community-update"
    data_cls = CommunityUpdateData

    pks = [
        # We generate a ComunityFile.id, just in case there was no logo before
        ("community_file", "id", generate_uuid),
    ]

    def _resolve_references(self, **kwargs):
        slug = self.data.community["slug"]
        state = STATE.COMMUNITIES.get(slug)
        self.data.community.setdefault("id", state["id"])

        # if it's also a logo update we need to resolve more PKs/FKs
        if self.data.community_file:
            self.data.old_object_version_id = state["logo_object_version_id"]
            self.data.object_version["bucket_id"] = state["bucket_id"]

            # If there was a logo already, we reuse the community file PK
            if state["community_file_id"]:
                self.data.community_file["id"] = state["community_file_id"]
            self.data.community_file["record_id"] = state["id"]

    def _generate_rows(self, **kwargs):
        """Generates rows for a new community."""
        yield Operation(OperationType.UPDATE, Community, self.data.community)

        # Not every community update has a logo
        if self.data.community_file:
            yield Operation(
                OperationType.INSERT,
                FilesInstance,
                self.data.file_instance,
            )

            # update the old object version also if there was one
            if self.data.old_object_version_id:
                yield Operation(
                    OperationType.UPDATE,
                    FilesObjectVersion,
                    {"version_id": self.data.old_object_version_id, "is_head": False},
                )

            yield Operation(
                OperationType.INSERT,
                FilesObjectVersion,
                self.data.object_version,
            )

            self.data.community_file["object_version_id"] = self.data.object_version[
                "version_id"
            ]
            if self.data.old_object_version_id:
                # If there was already a logo we UPDATE the community file
                yield Operation(
                    OperationType.UPDATE,
                    CommunityFile,
                    self.data.community_file,
                )
            else:
                # If no logo before we INSERT a community file
                yield Operation(
                    OperationType.INSERT,
                    CommunityFile,
                    self.data.community_file,
                )

            # Update the logo state
            STATE.COMMUNITIES.update(
                self.data.community["slug"],
                {
                    "community_file_id": self.data.community_file["id"],
                    "logo_object_version_id": self.data.object_version["version_id"],
                },
            )


@dataclass
class CommunityDeleteData(LoadData):
    """Community action data."""

    community: dict

    # Filled-in by the action
    oai_set_id: Optional[int] = None
    community_file_id: Optional[str] = None
    object_version_id: Optional[str] = None


class CommunityDeleteAction(LoadAction):
    """Delete a community."""

    name = "community-delete"
    data_cls = CommunityDeleteData

    def _resolve_references(self, **kwargs):
        slug = self.data.community["slug"]
        state = STATE.COMMUNITIES.get(slug)
        self.data.community.setdefault("id", state["id"])
        self.data.oai_set_id = state["oai_set_id"]
        self.data.community_file_id = state["community_file_id"]
        self.data.object_version_id = state["logo_object_version_id"]

    def _generate_rows(self, **kwargs):
        """Generates rows for deleting a communitoy."""
        # Only soft-delete by setting `json = NULL`
        self.data.community["json"] = None
        yield Operation(OperationType.UPDATE, Community, self.data.community)

        # Hard-delete the OAISet
        yield Operation(OperationType.DELETE, OAISet, {"id": self.data.oai_set_id})

        # Clean-up the logo also if there is one
        if self.data.community_file_id:
            yield Operation(
                OperationType.DELETE,
                FilesObjectVersion,
                {"version_id": self.data.object_version_id},
            )
            yield Operation(
                OperationType.DELETE,
                CommunityFile,
                {"id": self.data.community_file_id},
            )

        # NOTE: We don't update the state actually


class CommunityRecordAcceptAction(LoadAction):
    """Accept a record into a community."""

    # TODO: Implement
    pass


class CommunityRecordRejectAction(LoadAction):
    """Reject a record from a community."""

    # TODO: Implement
    pass


class CommunityRecordRemoveAction(LoadAction):
    """Remove a record from a community."""

    # TODO: Implement
    pass
