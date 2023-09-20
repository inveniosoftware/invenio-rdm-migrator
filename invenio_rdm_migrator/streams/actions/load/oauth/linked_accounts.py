# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth client applications actions module."""

from dataclasses import dataclass
from typing import Optional

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.oauth import RemoteAccount, RemoteToken, ServerClient, ServerToken
from ....models.users import UserIdentity


@dataclass
class OAuthLinkedAccountData(LoadData):
    """OAuth application action data."""

    remote_account: dict
    remote_token: dict
    user_identity: Optional[dict] = None
    server_token: Optional[dict] = None
    server_client: Optional[dict] = None


class OAuthLinkedAccountConnectAction(LoadAction):
    """Connect an external account."""

    name = "oauth-application-connect"
    data_cls = OAuthLinkedAccountData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        assert self.data.user_identity

        yield Operation(OperationType.INSERT, RemoteAccount, self.data.remote_account)
        yield Operation(OperationType.INSERT, RemoteToken, self.data.remote_token)
        yield Operation(OperationType.INSERT, UserIdentity, self.data.user_identity)

        if self.data.server_client:
            yield Operation(OperationType.INSERT, ServerClient, self.data.server_client)
        if self.data.server_token:
            yield Operation(OperationType.INSERT, ServerToken, self.data.server_token)


class OAuthLinkedAccountDisconnectAction(LoadAction):
    """Disonnect an external account."""

    name = "oauth-application-disconnect"
    data_cls = OAuthLinkedAccountData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        if self.data.user_identity:  # GH discconnet does not have it
            yield Operation(OperationType.DELETE, UserIdentity, self.data.user_identity)

        yield Operation(OperationType.DELETE, RemoteToken, self.data.remote_token)
        yield Operation(OperationType.DELETE, RemoteAccount, self.data.remote_account)


@dataclass
class OAuthGHTokenDisconnectData(LoadData):
    """OAuth GH disconnect token data."""

    token: dict
    user_identity: dict


class OAuthGHDisconnectToken(LoadAction):
    """Disconnect GH linked account server token and identity."""

    name = "oauth-gh-application-disconnect"
    data_cls = OAuthGHTokenDisconnectData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.DELETE, UserIdentity, self.data.user_identity)
        yield Operation(OperationType.DELETE, ServerToken, self.data.token)
