# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses user models to generate table rows."""

from dataclasses import InitVar, dataclass
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class FilesBucket(Model):
    """Files bucket dataclass model."""

    __tablename__: InitVar[str] = "files_bucket"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]
    updated: Mapped[str]
    default_location: Mapped[int]
    default_storage_class: Mapped[str]
    size: Mapped[int]
    quota_size: Mapped[int]
    max_file_size: Mapped[int]
    locked: Mapped[bool]
    deleted: Mapped[bool]


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

    __tablename__: InitVar[str] = "files_files"


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

    __tablename__: InitVar[str] = "files_object"
