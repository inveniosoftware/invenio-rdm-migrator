# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses OAuth models to generate table rows."""
from dataclasses import InitVar

from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class RemoteAccount(Model):
    """OAuth client remote account dataclass model."""

    __tablename__: InitVar[str] = "oauthclient_remoteaccount"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    client_id: Mapped[str]
    extra_data: Mapped[dict]
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
    client_id: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=True)
    website: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    client_secret: Mapped[str]  # it is text, migrated as is
    _redirect_uris: Mapped[str] = mapped_column(nullable=True)
    _default_scopes: Mapped[str] = mapped_column(nullable=True)
    is_internal: Mapped[bool] = mapped_column(nullable=True, default=False)
    is_confidential: Mapped[bool] = mapped_column(nullable=True, default=True)


class ServerToken(Model):
    """OAuth server token dataclass model."""

    __tablename__: InitVar[str] = "oauth2server_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str]
    user_id: Mapped[int] = mapped_column(nullable=True)
    access_token: Mapped[str] = mapped_column(nullable=True)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    expires: Mapped[str] = mapped_column(nullable=True)  # datetime
    _scopes: Mapped[str] = mapped_column(nullable=True)
    token_type: Mapped[str] = mapped_column(nullable=True, default="bearer")
    is_personal: Mapped[bool] = mapped_column(nullable=True, default=False)
    is_internal: Mapped[bool] = mapped_column(nullable=True, default=False)
