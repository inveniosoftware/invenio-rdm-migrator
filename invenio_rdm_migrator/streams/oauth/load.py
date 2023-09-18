# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration OAuth load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from ...load.postgresql.bulk.generators import (
    ExistingDataTableGenerator,
    SingleTableGenerator,
)
from ..models.oauth import RemoteAccount, RemoteToken, ServerClient, ServerToken


class OAuthClientCopyLoad(PostgreSQLCopyLoad):
    """OAuthClient loading of existing data."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                ExistingDataTableGenerator(tables=[RemoteAccount, RemoteToken]),
            ],
            **kwargs,
        )


class OAuthServerClientCopyLoad(PostgreSQLCopyLoad):
    """OAuth2Server clients loading."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[SingleTableGenerator(table=ServerClient)],
            **kwargs,
        )


class OAuthServerTokenCopyLoad(PostgreSQLCopyLoad):
    """OAuth2Server tokens loading."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[SingleTableGenerator(table=ServerToken)],
            **kwargs,
        )
