# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user table load module."""

from ...load.ids import generate_uuid, pid_pk
from ...load.postgresql.bulk.generators import TableGenerator
from ..models.communities import (
    Community,
    CommunityFile,
    CommunityMember,
    FeaturedCommunity,
)
from ..models.files import FilesBucket, FilesObjectVersion


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

    def __init__(self, communities_state):
        """Constructor."""
        self.communities_state = communities_state
        super().__init__(
            tables=[
                Community,
                CommunityMember,
                FeaturedCommunity,
                FilesBucket,
                FilesObjectVersion,
                CommunityFile,
            ],
            pks=[
                ("community.id", generate_uuid),
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
        community_files = data["community_files"]
        bucket = community_files["bucket"]

        if not self.communities_state.get(community_slug):
            self.communities_state.add(community_slug, {"id": community_id})

        community["bucket_id"] = bucket["id"]
        yield FilesBucket(**bucket)
        yield Community(**community)

        community_members = data["community_members"]
        for member in community_members:
            member["community_id"] = community_id
            yield CommunityMember(**member)

        featured_community = data["featured_community"]
        if featured_community.get("id"):
            featured_community["community_id"] = community_id
            yield FeaturedCommunity(**featured_community)

        community_file = community_files.get("file")
        # Not every community has a logo
        if community_file:
            file_object = community_files["file_object"]

            file_object["bucket_id"] = bucket["id"]
            file_object["file_id"] = community_file["id"]
            yield FilesObjectVersion(**file_object)

            community_file["record_id"] = community_id
            community_file["object_version_id"] = file_object["version_id"]
            yield CommunityFile(**community_file)
