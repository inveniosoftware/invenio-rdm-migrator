# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth2Server tokens actions module."""

from dataclasses import dataclass

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.oauth import ServerClient, ServerToken


@dataclass
class OAuthTokenData(LoadData):
    """Community action data."""

    client: dict
    token: dict


class OAuthTokenCreateAction(LoadAction):
    """Create a personal oauth token."""

    name = "oauth-server-token-create"
    data_cls = OAuthTokenData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.INSERT, ServerClient, self.data.client)
        yield Operation(OperationType.INSERT, ServerToken, self.data.token)
