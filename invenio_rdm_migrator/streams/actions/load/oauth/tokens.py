# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth2Server tokens actions module."""

from dataclasses import dataclass
from typing import Optional

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.oauth import ServerClient, ServerToken


@dataclass
class OAuthTokenData(LoadData):
    """OAuth server token action data."""

    client: Optional[dict] = None
    token: Optional[dict] = None


class OAuthServerTokenCreateAction(LoadAction):
    """Create a personal oauth token."""

    name = "oauth-server-token-create"
    data_cls = OAuthTokenData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        assert self.data.client and self.data.token

        yield Operation(OperationType.INSERT, ServerClient, self.data.client)
        yield Operation(OperationType.INSERT, ServerToken, self.data.token)


class OAuthServerTokenUpdateAction(LoadAction):
    """Create a personal oauth token."""

    name = "oauth-server-token-update"
    data_cls = OAuthTokenData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        if self.data.client:
            yield Operation(OperationType.UPDATE, ServerClient, self.data.client)
        if self.data.token:
            yield Operation(OperationType.UPDATE, ServerToken, self.data.token)


class OAuthServerTokenDeleteAction(LoadAction):
    """Create a personal oauth token."""

    name = "oauth-server-token-delete"
    data_cls = OAuthTokenData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        assert not self.data.client and self.data.token

        yield Operation(OperationType.DELETE, ServerToken, self.data.token)
