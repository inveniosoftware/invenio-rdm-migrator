# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses user models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class FilesBucket:
    """Files bucket dataclass model."""

    id: str
    created: str
    updated: str
    default_location: str
    default_storage_class: str
    size: int
    quota_size: int
    max_file_size: int
    locked: bool
    deleted: bool

    _table_name: InitVar[str] = "files_bucket"


@dataclass
class FilesInstance:
    """Files instance dataclass model."""

    id: str
    created: str
    updated: str
    uri: str
    storage_class: str
    size: int
    checksum: str
    readable: bool
    writable: bool
    last_check_at: str
    last_check: bool

    _table_name: InitVar[str] = "files_files"


@dataclass
class FilesObjectVersion:
    """Files object version dataclass model."""

    version_id: str
    created: str
    updated: str
    key: str
    bucket_id: str
    file_id: str
    _mimetype: str
    is_head: bool

    _table_name: InitVar[str] = "files_object"
