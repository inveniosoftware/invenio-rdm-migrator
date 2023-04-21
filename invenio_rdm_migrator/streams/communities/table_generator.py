# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user table load module."""
import random

from ...load.postgresql import TableGenerator, generate_uuid
from .models import Community, CommunityMember, FeaturedCommunity


def _generate_members_uuids(data):
    for member in data["community_members"]:
        member["id"] = generate_uuid(data)
    return data["community_members"]


def _generate_featured_community_id(data):
    if not data.get("featured_community"):
        return None
    return _pid_pk(data)


# keep track of generated PKs, since there's a chance they collide
GENERATED_PID_PKS = set()


def _pid_pk(data):
    """Generates a random integer between 1M and 2B, avoiding duplication with previously generated numbers."""
    lower_limit = 1_000_000
    upper_limit = 2_147_483_647 - 1

    while True:
        # we start at 1M to avoid collisions with existing low-numbered PKs
        val = random.randint(lower_limit, upper_limit)
        if val not in GENERATED_PID_PKS:
            GENERATED_PID_PKS.add(val)
            return val


class CommunityTableGenerator(TableGenerator):
    """User and related tables load."""

    def __init__(self, communities_cache):
        """Constructor."""
        self.communities_cache = communities_cache
        super().__init__(
            tables=[Community, CommunityMember, FeaturedCommunity],
            pks=[
                ("community.id", generate_uuid),
                ("community_members", _generate_members_uuids),
                ("featured_community.id", _generate_featured_community_id),
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

        featured_community = data["featured_community"]
        if featured_community.get("id"):
            featured_community["community_id"] = community_id
            yield FeaturedCommunity(**featured_community)

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass
