# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses models to generate table rows for OAI-PMH."""

from dataclasses import InitVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class WebhookEvent(Model):
    """Webhook event dataclass model."""

    __tablename__: InitVar[str] = "webhooks_events"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]
    updated: Mapped[str]
    receiver_id: Mapped[str]
    user_id: Mapped[int] = mapped_column(nullable=True)
    payload: Mapped[dict] = mapped_column(nullable=True)
    payload_headers: Mapped[dict] = mapped_column(nullable=True)
    response: Mapped[dict] = mapped_column(nullable=True)
    response_headers: Mapped[dict] = mapped_column(nullable=True)
    response_code: Mapped[int] = mapped_column(nullable=True)


class Repository(Model):
    """Repository dataclass model."""

    __tablename__: InitVar[str] = "github_repositories"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[str]
    updated: Mapped[str]
    github_id: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(nullable=True)
    hook: Mapped[int] = mapped_column(nullable=True)


class Release(Model):
    """Release dataclass model."""

    __tablename__: InitVar[str] = "github_releases"

    created: Mapped[str]
    updated: Mapped[str]
    id: Mapped[UUID] = mapped_column(primary_key=True)
    release_id: Mapped[int] = mapped_column(nullable=True)
    tag: Mapped[str] = mapped_column(nullable=True)
    errors: Mapped[dict] = mapped_column(nullable=True)
    repository_id: Mapped[UUID] = mapped_column(nullable=True)
    event_id: Mapped[UUID] = mapped_column(nullable=True)
    record_id: Mapped[UUID] = mapped_column(nullable=True)
    status: Mapped[str]
