# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses user models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class User:
    """User dataclass model."""

    id: int
    created: str
    updated: str
    username: str
    displayname: str
    email: str
    password: str
    active: bool
    confirmed_at: str
    version_id: int
    profile: dict
    preferences: dict

    _table_name: InitVar[str] = "accounts_user"


@dataclass
class LoginInformation:
    """Login information dataclass model."""

    user_id: int
    last_login_at: str
    current_login_at: str
    last_login_ip: str
    current_login_ip: str
    login_count: int

    _table_name: InitVar[str] = "accounts_user_login_information"


@dataclass
class SessionActivity:
    """Session activity dataclass model."""

    user_id: int
    created: str
    updated: str
    sid_s: str
    ip: str
    country: str
    browser: str
    browser_version: str
    os: str
    device: str

    _table_name: InitVar[str] = "accounts_user_session_activity"


@dataclass
class Tokens:
    """OAuth server tokens dataclass model."""

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


@dataclass
class UserIdentity:
    """User identity dataclass model."""

    created: str
    updated: str
    id: str
    method: str
    id_user: int

    _table_name: InitVar[str] = "accounts_useridentity"
