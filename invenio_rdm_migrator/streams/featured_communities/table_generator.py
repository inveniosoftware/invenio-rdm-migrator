# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Invenio RDM migration featured community table generator module."""

import random

from ...load.postgresql import TableGenerator
from .models import FeaturedCommunity

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


class FeaturedCommunityTableGenerator(TableGenerator):
    """User and related tables load."""

    def __init__(self, communities_cache):
        """Constructor."""
        self.communities_cache = communities_cache
        super().__init__(
            tables=[FeaturedCommunity],
            pks=[
                (
                    "featured_community.id",
                    _pid_pk,
                ),
            ],
        )

    def _generate_rows(self, data, **kwargs):
        """Generates featured community rows to be loaded."""
        featured_community = data["featured_community"]
        community_slug = featured_community.pop("slug", None)

        community_uuid = self.communities_cache.get(community_slug)
        if community_uuid is None:
            return None  # TODO what happens if the community is not added in cache yet?

        featured_community["community_id"] = community_uuid

        yield FeaturedCommunity(**featured_community)

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass
