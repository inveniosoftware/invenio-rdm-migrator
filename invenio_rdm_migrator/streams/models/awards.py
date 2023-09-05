# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Awards models."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class Awards(Model):
    """Awards dataclass model."""

    __tablename__: InitVar[str] = "award_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    pid: Mapped[str]
    json: Mapped[dict]
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
