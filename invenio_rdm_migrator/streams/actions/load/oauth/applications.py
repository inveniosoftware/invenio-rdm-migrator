# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth2Server applications actions module."""

from dataclasses import dataclass

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.oauth import ServerClient


@dataclass
class OAuthApplicationData(LoadData):
    """OAuth application action data."""

    client: dict


class OAuthApplicationCreateAction(LoadAction):
    """Create a application auth."""

    name = "oauth-application-create"
    data_cls = OAuthApplicationData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.INSERT, ServerClient, self.data.client)


class OAuthApplicationUpdateAction(LoadAction):
    """Update a application auth.

    Note a client secret reset can be treated as an update.
    """

    name = "oauth-application-update"
    data_cls = OAuthApplicationData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.UPDATE, ServerClient, self.data.client)


class OAuthApplicationDeleteAction(LoadAction):
    """Delete a application auth."""

    name = "oauth-application-delete"
    data_cls = OAuthApplicationData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new oauth token."""
        yield Operation(OperationType.DELETE, ServerClient, self.data.client)
