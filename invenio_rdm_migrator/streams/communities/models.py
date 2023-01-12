# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses user models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class Community:
    """Community dataclass model."""

    id: str
    created: str
    updated: str
    json: dict
    version_id: int
    slug: str
    bucket_id: str

    _table_name: InitVar[str] = "communities_metadata"


@dataclass
class CommunityMember:
    """Community members dataclass model."""

    id: str
    created: str
    updated: str
    json: dict
    version_id: int
    role: str
    visible: bool
    active: bool
    community_id: str
    user_id: int
    group_id: int
    request_id: int

    _table_name: InitVar[str] = "communities_members"
