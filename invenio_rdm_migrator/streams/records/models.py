# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses record models to generate table rows."""

from dataclasses import InitVar, dataclass


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

    _table_name: InitVar[str] = "rdm_records_metadata"


@dataclass
class RDMParentMetadata:
    """RDM Parent Metadata dataclass model."""

    id: str
    json: dict
    created: str
    updated: str
    version_id: int

    _table_name: InitVar[str] = "rdm_parents_metadata"


@dataclass
class RDMVersionState:
    """RDM Version State dataclass model."""

    latest_index: int
    parent_id: str
    latest_id: str
    next_draft_id: str

    _table_name: InitVar[str] = "rdm_versions_state"


@dataclass
class RDMDraftMetadata:
    """RDM Draft Metadata dataclass model."""

    id: str
    json: dict
    created: str
    updated: str
    version_id: int
    index: int
    bucket_id: str
    parent_id: str

    expires_at: str
    fork_version_id: int

    _table_name: InitVar[str] = "rdm_drafts_metadata"


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

    _table_name: InitVar[str] = "rdm_records_files"


@dataclass
class RDMDraftFile(RDMRecordFile):
    """RDM Draft File dataclass model."""

    _table_name: InitVar[str] = "rdm_drafts_files"
