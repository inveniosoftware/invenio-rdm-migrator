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
    """OAuthClient loading of existing data.

    It does not load the two tables with tokens, since they need rehashing.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                # it passes on prepare so entries wont have an effect on it
                ExistingDataTableGenerator(tables=[RemoteAccount]),
                # this tg will treat the entries passing through the stream
                SingleTableGenerator(table=RemoteToken),
            ],
            **kwargs
        )


class OAuthServerCopyLoad(PostgreSQLCopyLoad):
    """OAuth2Server loading of existing data.

    It does not load the two tables with tokens, since they need rehashing.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                # it passes on prepare so entries wont have an effect on it
                ExistingDataTableGenerator(tables=[ServerClient]),
                # this tg will treat the entries passing through the stream
                SingleTableGenerator(table=ServerToken),
            ],
            **kwargs
        )
