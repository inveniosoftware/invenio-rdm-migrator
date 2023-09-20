# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration load actions."""

from .communities import (
    CommunityCreateAction,
    CommunityDeleteAction,
    CommunityUpdateAction,
)
from .drafts import DraftCreateAction, DraftEditAction, DraftPublishAction
from .files import DraftFileUploadAction
from .github import HookEventCreateAction, HookEventUpdateAction, HookRepoUpdateAction
from .oauth import (
    OAuthApplicationCreateAction,
    OAuthApplicationDeleteAction,
    OAuthApplicationUpdateAction,
    OAuthGHDisconnectToken,
    OAuthLinkedAccountConnectAction,
    OAuthLinkedAccountDisconnectAction,
    OAuthServerTokenCreateAction,
    OAuthServerTokenDeleteAction,
    OAuthServerTokenUpdateAction,
)
from .users import UserDeactivationAction, UserEditAction, UserRegistrationAction

__all__ = (
    "CommunityCreateAction",
    "CommunityDeleteAction",
    "CommunityUpdateAction",
    "DraftCreateAction",
    "DraftEditAction",
    "DraftFileUploadAction",
    "DraftPublishAction",
    "HookEventCreateAction",
    "HookEventUpdateAction",
    "HookRepoUpdateAction",
    "OAuthApplicationCreateAction",
    "OAuthApplicationDeleteAction",
    "OAuthApplicationUpdateAction",
    "OAuthGHDisconnectToken",
    "OAuthLinkedAccountConnectAction",
    "OAuthLinkedAccountDisconnectAction",
    "OAuthServerTokenCreateAction",
    "OAuthServerTokenDeleteAction",
    "OAuthServerTokenUpdateAction",
    "UserDeactivationAction",
    "UserEditAction",
    "UserRegistrationAction",
)
