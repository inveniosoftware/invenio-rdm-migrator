# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Requests models."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class RequestMetadata(Model):
    """RDM Record File dataclass model."""

    __tablename__: InitVar[str] = "request_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict] = mapped_column(nullable=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    number: Mapped[str]
    expires_at: Mapped[str]  # datetime
