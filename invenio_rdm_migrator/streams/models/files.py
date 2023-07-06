# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Files models."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class FilesBucket(Model):
    """Files bucket dataclass model."""

    __tablename__: InitVar[str] = "files_bucket"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    default_location: Mapped[int]
    default_storage_class: Mapped[str]
    size: Mapped[int]
    quota_size: Mapped[int]
    max_file_size: Mapped[int]
    locked: Mapped[bool]
    deleted: Mapped[bool]


class FilesInstance(Model):
    """Files instance dataclass model."""

    __tablename__: InitVar[str] = "files_files"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    uri: Mapped[str]
    storage_class: Mapped[str]
    size: Mapped[int]
    checksum: Mapped[str]
    readable: Mapped[bool]
    writable: Mapped[bool]
    last_check_at: Mapped[str]  # datetime
    last_check: Mapped[bool]


class FilesObjectVersion(Model):
    """Files object version dataclass model."""

    __tablename__: InitVar[str] = "files_object"

    version_id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    key: Mapped[str]
    bucket_id: Mapped[UUID]
    file_id: Mapped[UUID]
    _mimetype: Mapped[str]
    is_head: Mapped[bool]
