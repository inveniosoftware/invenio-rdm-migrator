# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration GitHub load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from ...load.postgresql.bulk.generators import ExistingDataTableGenerator
from ..models.github import Repository, WebhookEvent
from .table_generator import ReleaseTableGenerator


class ExistingWebhookEventsCopyLoad(PostgreSQLCopyLoad):
    """Webhook events loading of existing data."""

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[
                # it passes on prepare so entries wont have an effect on it
                ExistingDataTableGenerator(tables=[WebhookEvent], pks=[]),
            ],
            data_dir=data_dir,
            existing_data=True,
            # **kwargs
        )


class ExistingGitHubRepositoriesCopyLoad(PostgreSQLCopyLoad):
    """GitHub repository loading of existing data."""

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[
                # it passes on prepare so entries wont have an effect on it
                ExistingDataTableGenerator(tables=[Repository], pks=[]),
            ],
            data_dir=data_dir,
            existing_data=True,
            # **kwargs
        )


class GitHubReleasesCopyLoad(PostgreSQLCopyLoad):
    """GitHub release loading of existing data."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                # this tg will treat the entries passing through the stream
                ReleaseTableGenerator(),
            ],
            **kwargs
        )
