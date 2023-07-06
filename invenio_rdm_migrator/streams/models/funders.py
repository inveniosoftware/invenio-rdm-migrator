# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Funders models."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class Funders(Model):
    """Funders dataclass model."""

    __tablename__: InitVar[str] = "funder_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    pid: Mapped[str]
    json: Mapped[dict] = mapped_column(JSONB())
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
