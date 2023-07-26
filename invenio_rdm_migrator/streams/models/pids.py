# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses models to generate table rows."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class PersistentIdentifier(Model):
    """Persistent identifier dataclass model."""

    __tablename__ = "pidstore_pid"

    id: Mapped[int] = mapped_column(primary_key=True)
    pid_type: Mapped[str]
    pid_value: Mapped[str]
    status: Mapped[str]
    object_type: Mapped[str] = mapped_column(nullable=True)
    object_uuid: Mapped[UUID] = mapped_column(nullable=True)
    created: Mapped[str]
    updated: Mapped[str]
    # default since we do not take it into account in many places
    # ant it's not in the data
    pid_provider: Mapped[str] = mapped_column(nullable=True, default=None)
