# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses record models to generate table rows."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class RDMRecordMetadata(Model):
    """RDM Record Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_records_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    index: Mapped[int]
    bucket_id: Mapped[UUID]
    parent_id: Mapped[UUID]
    deletion_status: Mapped[str]
    media_bucket_id: Mapped[UUID] = mapped_column(nullable=True, default=None)


class RDMParentMetadata(Model):
    """RDM Parent Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_parents_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]


class RDMVersionState(Model):
    """RDM Version State dataclass model."""

    __tablename__: InitVar[str] = "rdm_versions_state"

    parent_id: Mapped[UUID] = mapped_column(primary_key=True)
    latest_id: Mapped[UUID] = mapped_column(nullable=True)
    next_draft_id: Mapped[UUID] = mapped_column(nullable=True)
    # latest_index has a programmatic default of 1 if the db value is None
    latest_index: Mapped[int] = mapped_column(nullable=True)


class RDMDraftMetadata(Model):
    """RDM Draft Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_drafts_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    index: Mapped[int]
    bucket_id: Mapped[UUID]
    parent_id: Mapped[UUID]
    expires_at: Mapped[str]
    # in a new version this value is None
    fork_version_id: Mapped[int] = mapped_column(nullable=True)
    media_bucket_id: Mapped[UUID] = mapped_column(nullable=True, default=None)


class RDMRecordFile(Model):
    """RDM Record File dataclass model."""

    __tablename__: InitVar[str] = "rdm_records_files"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict]
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    key: Mapped[str]
    record_id: Mapped[UUID]
    object_version_id: Mapped[UUID]


class RDMRecordMediaFile(Model):
    """RDM Record Media File dataclass model."""

    __tablename__: InitVar[str] = "rdm_records_media_files"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    key: Mapped[str]
    record_id: Mapped[UUID]
    object_version_id: Mapped[UUID]


class RDMDraftFile(Model):
    """RDM Draft File dataclass model."""

    __tablename__: InitVar[str] = "rdm_drafts_files"

    # duplicated code to avoid dealing with sqlalchemy inheritance and fks
    # which in our case do not play any role
    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    key: Mapped[str]
    record_id: Mapped[UUID]
    object_version_id: Mapped[UUID] = mapped_column(nullable=True)


class RDMDraftMediaFile(Model):
    """RDM Draft Media File dataclass model."""

    __tablename__: InitVar[str] = "rdm_drafts_media_files"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    key: Mapped[str]
    record_id: Mapped[UUID]
    object_version_id: Mapped[UUID] = mapped_column(nullable=True)
