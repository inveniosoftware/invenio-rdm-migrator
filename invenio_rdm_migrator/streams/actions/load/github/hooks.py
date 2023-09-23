# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GitHub hooks actions module."""

from dataclasses import dataclass

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.github import Repository, WebhookEvent


@dataclass
class RepoData(LoadData):
    """GitHub repository action data."""

    gh_repository: dict


class RepoCreateAction(LoadAction):
    """Create a GitHub repository."""

    name = "gh-repo-create"
    data_cls = RepoData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo create."""
        yield Operation(OperationType.INSERT, Repository, self.data.gh_repository)


class RepoUpdateAction(LoadAction):
    """Update a GitHub repository."""

    name = "gh-repo-update"
    data_cls = RepoData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        # assumes the repo was created (INSERT) during repository sync or enable/create
        yield Operation(OperationType.UPDATE, Repository, self.data.gh_repository)


# NOTE: hook enabling happens in two phases, most likely due to multiple session commits
# the first assigned a hook id to the repository, the second updates the oauth server
# token and creates the actual webhook event.


@dataclass
class HookData(LoadData):
    """GitHub event hook action data."""

    webhook_event: dict


class HookEventCreateAction(LoadAction):
    """Create the webhook event in a GitHub repository."""

    name = "gh-hook-event-create"
    data_cls = HookData

    def _generate_rows(self, **kwargs):
        """Generates rows for the second phase of enabling a gh repo webhook."""
        yield Operation(OperationType.INSERT, WebhookEvent, self.data.webhook_event)


class HookEventUpdateAction(LoadAction):
    """Update the webhook event."""

    name = "gh-hook-event-update"
    data_cls = HookData

    def _generate_rows(self, **kwargs):
        """Generates rows for a webhook event update."""
        yield Operation(OperationType.UPDATE, WebhookEvent, self.data.webhook_event)
