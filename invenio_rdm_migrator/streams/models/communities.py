# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities models."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class Community(Model):
    """Community dataclass model."""

    __tablename__: InitVar[str] = "communities_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    json: Mapped[dict] = mapped_column(nullable=True)
    version_id: Mapped[int]
    slug: Mapped[str]
    bucket_id: Mapped[UUID] = mapped_column(primary_key=True)


class RDMParentCommunityMetadata(Model):
    """RDM Community Parent Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_parents_community"

    community_id: Mapped[UUID] = mapped_column(primary_key=True)
    record_id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID]


class CommunityMember(Model):
    """Community members dataclass model."""

    __tablename__: InitVar[str] = "communities_members"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    json: Mapped[dict] = mapped_column(nullable=True)
    version_id: Mapped[int]
    role: Mapped[str]
    visible: Mapped[bool]
    active: Mapped[bool]
    community_id: Mapped[UUID]
    user_id: Mapped[int]
    group_id: Mapped[int] = mapped_column(nullable=True)
    request_id: Mapped[UUID] = mapped_column(nullable=True)


class FeaturedCommunity(Model):
    """Featured community dataclass model."""

    __tablename__: InitVar[str] = "communities_featured"

    community_id: Mapped[UUID]
    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    start_date: Mapped[str]  # datetime


class CommunityFile(Model):
    """Community file dataclass model."""

    __tablename__: InitVar[str] = "communities_files"

    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    version_id: Mapped[int]
    key: Mapped[str] = mapped_column(primary_key=True)
    record_id: Mapped[UUID]
    object_version_id: Mapped[UUID]
