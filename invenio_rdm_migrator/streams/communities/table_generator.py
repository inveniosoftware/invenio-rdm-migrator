# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user table load module."""

from ...load.postgresql import TableGenerator, generate_uuid
from .models import Community, CommunityMember


def _generate_members_uuids(data):
    for member in data["community_members"]:
        member["id"] = generate_uuid()
    return data["community_members"]


class CommunityTableGenerator(TableGenerator):
    """User and related tables load."""

    def __init__(self, communities_cache):
        """Constructor."""
        self.communities_cache = communities_cache
        super().__init__(
            tables=[Community, CommunityMember],
            pks=[
                ("community.id", generate_uuid),
                ("community_members", _generate_members_uuids),
            ],
        )

    def _generate_rows(self, data, **kwargs):
        community = data["community"]
        community_id = community["id"]
        community_slug = community["slug"]
        if self.communities_cache.get(community_slug) is None:
            self.communities_cache[community_slug] = community_id

        yield Community(**community)

        community_members = data["community_members"]
        for member in community_members:
            member["community_id"] = community_id
            yield CommunityMember(**member)

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass
