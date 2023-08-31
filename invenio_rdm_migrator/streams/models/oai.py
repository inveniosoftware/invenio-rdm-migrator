# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses models to generate table rows for OAI-PMH."""

from dataclasses import InitVar

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class OAISet(Model):
    """OAI set dataclass model."""

    __tablename__: InitVar[str] = "oaiserver_set"

    id: Mapped[int] = mapped_column(primary_key=True)
    spec: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    search_pattern: Mapped[str] = mapped_column(nullable=True)
    system_created: Mapped[bool] = mapped_column(nullable=False)

    created: Mapped[str]
    updated: Mapped[str]
