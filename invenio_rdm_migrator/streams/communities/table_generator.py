# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user table load module."""

from ...load.ids import generate_pk_for, generate_uuid, pid_pk
from ...load.postgresql.bulk.generators import TableGenerator
from ...state import STATE
from ..models.communities import (
    Community,
    CommunityFile,
    CommunityMember,
    FeaturedCommunity,
)
from ..models.files import FilesBucket, FilesObjectVersion
from ..models.oai import OAISet


def _generate_members_uuids(data):
    for member in data["community_members"]:
        member["id"] = generate_uuid(data)
    return data["community_members"]


def _generate_featured_community_id(data):
    if not data.get("featured_community"):
        return None
    return pid_pk()


class CommunityTableGenerator(TableGenerator):
    """User and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                Community,
                CommunityMember,
                FeaturedCommunity,
                OAISet,
                FilesBucket,
                FilesObjectVersion,
                CommunityFile,
            ],
            pks=[
                ("community.id", generate_uuid),
                ("oai_set.id", generate_pk_for(OAISet)),
                ("community_members", _generate_members_uuids),
                ("featured_community.id", _generate_featured_community_id),
                ("community_files.file_object.version_id", generate_uuid),
                ("community_files.bucket.id", generate_uuid),
            ],
        )

    def _generate_rows(self, data, **kwargs):
        community = data["community"]
        community_id = community["id"]
        community_slug = community["slug"]
        community_oai_set = data["oai_set"]
        community_files = data["community_files"]
        bucket = community_files["bucket"]

        community["bucket_id"] = bucket["id"]
        yield FilesBucket(**bucket)
        yield Community(**community)

        community_oai_set["search_pattern"] = f"parent.communities.ids:{community_id}"
        community_oai_set["system_created"] = True
        yield OAISet(**community_oai_set)

        community_members = data["community_members"]
        for member in community_members:
            member["community_id"] = community_id
            yield CommunityMember(**member)

        featured_community = data["featured_community"]
        if featured_community.get("id"):
            featured_community["community_id"] = community_id
            yield FeaturedCommunity(**featured_community)

        community_file = community_files.get("file")
        file_object = community_files.get("file_object")
        # Not every community has a logo
        if community_file:
            file_object["bucket_id"] = bucket["id"]
            file_object["file_id"] = community_file["id"]
            yield FilesObjectVersion(**file_object)

            community_file["record_id"] = community_id
            community_file["object_version_id"] = file_object["version_id"]
            yield CommunityFile(**community_file)

        if not STATE.COMMUNITIES.get(community_slug):
            STATE.COMMUNITIES.add(
                community_slug,
                {
                    "id": community_id,
                    "bucket_id": bucket["id"],
                    "oai_set_id": community_oai_set["id"],
                    "community_file_id": (community_file or {}).get("id"),
                    "logo_object_version_id": (file_object or {}).get("version_id"),
                },
            )
