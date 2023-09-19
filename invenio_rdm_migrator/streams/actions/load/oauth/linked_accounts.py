# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth client applications actions module."""

from dataclasses import dataclass

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.oauth import RemoteAccount, RemoteToken
from ....models.users import UserIdentity


@dataclass
class OAuthLinkedAccountData(LoadData):
    """OAuth application action data."""

    remote_account: dict
    remote_token: dict
    user_identity: dict


class OAuthLinkedAccountConnectAction(LoadAction):
    """Connect an external account."""

    name = "oauth-application-connect"
    data_cls = OAuthLinkedAccountData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.INSERT, RemoteAccount, self.data.remote_account)
        yield Operation(OperationType.INSERT, RemoteToken, self.data.remote_token)
        yield Operation(OperationType.INSERT, UserIdentity, self.data.user_identity)


class OAuthLinkedAccountDisconnectAction(LoadAction):
    """Disonnect an external account."""

    name = "oauth-application-disconnect"
    data_cls = OAuthLinkedAccountData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.DELETE, UserIdentity, self.data.user_identity)
        yield Operation(OperationType.DELETE, RemoteToken, self.data.remote_token)
        yield Operation(OperationType.DELETE, RemoteAccount, self.data.remote_account)
