# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses user models to generate table rows."""

from dataclasses import InitVar

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ...load.postgresql.models import Model


class User(Model):
    """User dataclass model."""

    __tablename__: InitVar[str] = "accounts_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    username: Mapped[str]
    displayname: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    active: Mapped[bool]
    updated: Mapped[str]  # datetime
    version_id: Mapped[int]
    profile: Mapped[dict] = mapped_column(JSONB())
    preferences: Mapped[dict] = mapped_column(JSONB())


class LoginInformation(Model):
    """Login information dataclass model."""

    __tablename__: InitVar[str] = "accounts_user_login_information"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    last_login_at: Mapped[str]  # datetime
    current_login_at: Mapped[str]  # datetime
    last_login_ip: Mapped[str]
    current_login_ip: Mapped[str]
    login_count: Mapped[int]


class SessionActivity(Model):
    """Session activity dataclass model."""

    __tablename__: InitVar[str] = "accounts_user_session_activity"

    user_id: Mapped[int]
    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    sid_s: Mapped[str] = mapped_column(primary_key=True)
    ip: Mapped[str]
    country: Mapped[str]
    browser: Mapped[str]
    browser_version: Mapped[str]
    os: Mapped[str]
    device: Mapped[str]


class UserIdentity(Model):
    """User identity dataclass model."""

    __tablename__: InitVar[str] = "accounts_useridentity"

    created: Mapped[str]  # datetime
    updated: Mapped[str]  # datetime
    id: Mapped[str] = mapped_column(primary_key=True)
    method: Mapped[str] = mapped_column(primary_key=True)
    id_user: Mapped[int]
