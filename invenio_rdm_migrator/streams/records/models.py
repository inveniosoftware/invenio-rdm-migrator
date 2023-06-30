# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses record models to generate table rows."""

from dataclasses import InitVar, dataclass
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


@dataclass
class RDMRecordMetadata:
    """RDM Record Metadata dataclass model."""

    id: str
    json: dict
    created: str
    updated: str
    version_id: int
    index: int
    bucket_id: str
    parent_id: str

    __tablename__: InitVar[str] = "rdm_records_metadata"


class RDMParentMetadata(Model):
    """RDM Parent Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_parents_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(JSONB())
    created: Mapped[str]
    updated: Mapped[str]
    version_id: Mapped[int]


class RDMVersionState(Model):
    """RDM Version State dataclass model."""

    __tablename__: InitVar[str] = "rdm_versions_state"

    latest_index: Mapped[int]
    parent_id: Mapped[UUID] = mapped_column(primary_key=True)
    latest_id: Mapped[UUID]
    next_draft_id: Mapped[UUID]


class RDMDraftMetadata(Model):
    """RDM Draft Metadata dataclass model."""

    __tablename__: InitVar[str] = "rdm_drafts_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(JSONB())
    created: Mapped[str]
    updated: Mapped[str]
    version_id: Mapped[int]
    index: Mapped[int]
    bucket_id: Mapped[UUID]
    parent_id: Mapped[UUID]
    expires_at: Mapped[str]
    fork_version_id: Mapped[int]


@dataclass
class RDMRecordFile:
    """RDM Record File dataclass model."""

    id: str
    json: dict
    created: str
    updated: str
    version_id: int
    key: str
    record_id: str
    object_version_id: str

    __tablename__: InitVar[str] = "rdm_records_files"


@dataclass
class RDMDraftFile(RDMRecordFile):
    """RDM Draft File dataclass model."""

    __tablename__: InitVar[str] = "rdm_drafts_files"
