# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration OAuth2Server action stream."""

from .applications import (
    OAuthApplicationCreateAction,
    OAuthApplicationDeleteAction,
    OAuthApplicationUpdateAction,
)
from .linked_accounts import (
    OAuthGHDisconnectToken,
    OAuthLinkedAccountConnectAction,
    OAuthLinkedAccountDisconnectAction,
)
from .tokens import (
    OAuthServerTokenCreateAction,
    OAuthServerTokenDeleteAction,
    OAuthServerTokenUpdateAction,
)

__all__ = (
    "OAuthApplicationCreateAction",
    "OAuthApplicationDeleteAction",
    "OAuthApplicationUpdateAction",
    "OAuthGHDisconnectToken",
    "OAuthLinkedAccountConnectAction",
    "OAuthLinkedAccountDisconnectAction",
    "OAuthServerTokenCreateAction",
    "OAuthServerTokenDeleteAction",
    "OAuthServerTokenUpdateAction",
)
