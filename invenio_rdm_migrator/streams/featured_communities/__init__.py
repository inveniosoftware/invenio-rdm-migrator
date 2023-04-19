# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Invenio RDM migration featured communities stream."""

from .load import FeaturedCommunityCopyLoad
from .transform import FeaturedCommunityEntry, FeaturedCommunityTransform

__all__ = (
    "FeaturedCommunityCopyLoad",
    "FeaturedCommunityEntry",
    "FeaturedCommunityTransform",
)
