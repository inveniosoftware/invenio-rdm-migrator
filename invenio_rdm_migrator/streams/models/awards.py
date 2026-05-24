# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Awards models."""

from dataclasses import InitVar
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class Awards(Model):
    """Awards dataclass model."""

    __tablename__: InitVar[str] = "award_metadata"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    pid: Mapped[str]
    json: Mapped[dict]
    created: Mapped[datetime]
    updated: Mapped[datetime]
    version_id: Mapped[int]
