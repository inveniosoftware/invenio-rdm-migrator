# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Files models."""

from dataclasses import InitVar
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from ...load.postgresql.models import Model


class FilesBucket(Model):
    """Files bucket dataclass model."""

    __tablename__: InitVar[str] = "files_bucket"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[datetime]
    updated: Mapped[datetime]
    default_location: Mapped[int]
    default_storage_class: Mapped[str]
    size: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    locked: Mapped[bool]
    deleted: Mapped[bool]
    quota_size: Mapped[int] = mapped_column(BigInteger(), nullable=True)
    max_file_size: Mapped[int] = mapped_column(BigInteger(), nullable=True)


class FilesInstance(Model):
    """Files instance dataclass model."""

    __tablename__: InitVar[str] = "files_files"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[datetime]
    updated: Mapped[datetime]
    uri: Mapped[str] = mapped_column(nullable=True)
    storage_class: Mapped[str] = mapped_column(nullable=True)
    size: Mapped[int] = mapped_column(BigInteger(), nullable=True)
    checksum: Mapped[str] = mapped_column(nullable=True)
    readable: Mapped[bool]
    writable: Mapped[bool]
    last_check_at: Mapped[datetime] = mapped_column(nullable=True)
    last_check: Mapped[bool]


class FilesObjectVersion(Model):
    """Files object version dataclass model."""

    __tablename__: InitVar[str] = "files_object"

    version_id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[datetime]
    updated: Mapped[datetime]
    key: Mapped[str]
    bucket_id: Mapped[UUID]
    file_id: Mapped[UUID] = mapped_column(nullable=True)
    _mimetype: Mapped[str] = mapped_column(nullable=True)
    is_head: Mapped[bool]
