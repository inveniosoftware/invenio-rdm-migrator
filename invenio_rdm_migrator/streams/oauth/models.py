# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses OAuth models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class RemoteAccount:
    """OAuth client remote account dataclass model."""

    id: int
    user_id: int
    client_id: str
    extra_data: dict
    created: str
    updated: str

    _table_name: InitVar[str] = "oauthclient_remoteaccount"


@dataclass
class RemoteToken:
    """OAuth client remote token dataclass model."""

    id_remote_account: int
    token_type: str
    access_token: bytes
    secret: str
    created: str
    updated: str

    _table_name: InitVar[str] = "oauthclient_remotetoken"


@dataclass
class UserIdentity:
    """OAuth client user identity dataclass model."""

    id: str
    method: str
    id_user: int
    created: str
    updated: str

    _table_name: InitVar[str] = "oauthclient_useridentity"


@dataclass
class ServerClient:
    """OAuth server client dataclass model."""

    name: str
    description: str
    website: str
    user_id: int
    client_id: str
    client_secret: str  # it is text, migrated as is
    is_confidential: bool
    is_internal: bool
    _redirect_uris: str
    _default_scopes: str

    _table_name: InitVar[str] = "oauth2server_client"


@dataclass
class ServerToken:
    """OAuth server token dataclass model."""

    id: int
    client_id: str
    user_id: int
    token_type: str
    access_token: bytes
    refresh_token: bytes
    expires: str
    _scopes: str
    is_personal: bool
    is_internal: bool

    _table_name: InitVar[str] = "oauth2server_token"
