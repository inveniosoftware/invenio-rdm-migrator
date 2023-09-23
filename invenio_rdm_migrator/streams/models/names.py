# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Name model."""

from dataclasses import InitVar
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class Name(Model):
    """Funders dataclass model."""

    __tablename__: InitVar[str] = "name_metadata"

    created: Mapped[datetime]
    updated: Mapped[datetime]
    id: Mapped[UUID] = mapped_column(primary_key=True)
    json: Mapped[dict]
    version_id: Mapped[int]
    pid: Mapped[str]
