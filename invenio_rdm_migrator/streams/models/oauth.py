# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses OAuth models to generate table rows."""
from dataclasses import InitVar

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class RemoteAccount(Model):
    """OAuth client remote account dataclass model."""

    __tablename__: InitVar[str] = "oauthclient_remoteaccount"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    client_id: Mapped[str]
    extra_data: Mapped[dict] = mapped_column(JSONB())
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime


class RemoteToken(Model):
    """OAuth client remote token dataclass model."""

    __tablename__: InitVar[str] = "oauthclient_remotetoken"

    id_remote_account: Mapped[int] = mapped_column(primary_key=True)
    token_type: Mapped[str] = mapped_column(primary_key=True)
    access_token: Mapped[bytes]
    secret: Mapped[str]
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime


class ServerClient(Model):
    """OAuth server client dataclass model."""

    __tablename__: InitVar[str] = "oauth2server_client"

    name: Mapped[str]
    description: Mapped[str]
    website: Mapped[str]
    user_id: Mapped[int]
    client_id: Mapped[str] = mapped_column(primary_key=True)
    client_secret: Mapped[str]  # it is text, migrated as is
    is_confidential: Mapped[bool]
    is_internal: Mapped[bool]
    _redirect_uris: Mapped[str]
    _default_scopes: Mapped[str]


class ServerToken(Model):
    """OAuth server token dataclass model."""

    __tablename__: InitVar[str] = "oauth2server_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str]
    user_id: Mapped[int]
    token_type: Mapped[str]
    access_token: Mapped[bytes]
    refresh_token: Mapped[bytes]
    expires: Mapped[str]  # datetime
    _scopes: Mapped[str]
    is_personal: Mapped[bool]
    is_internal: Mapped[bool]
