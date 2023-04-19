# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Dataclasses featured community models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class FeaturedCommunity:
    """Featured community dataclass model."""

    community_id: str
    id: str
    created: str
    updated: str
    start_date: str

    _table_name: InitVar[str] = "communities_featured"
