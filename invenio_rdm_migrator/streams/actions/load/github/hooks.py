# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GitHub hooks actions module."""

from dataclasses import dataclass
from typing import Optional

from .....actions import LoadAction, LoadData
from .....load.postgresql.transactions.operations import Operation, OperationType
from ....models.github import Repository, WebhookEvent
from ....models.oauth import ServerToken


@dataclass
class HookData(LoadData):
    """GitHub event hook action data."""

    gh_repository: Optional[dict] = None
    oauth_token: Optional[dict] = None
    webhook_event: Optional[dict] = None


# note: hook enabling happens in two phases, most likely due to multiple session commits
# the first assigned a hook id to the repository, the second updates the oauth server
# token and creates the actual webhook event.


class HookRepoUpdateAction(LoadAction):
    """Update the webhook in a GitHub repository.

    This will serve for hook enabling first phase and for disabling, as well as for
    normal repository updates.
    """

    name = "gh-hook-repo-update"
    data_cls = HookData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        assert self.data.gh_repository
        # assumes the repo was created (INSERT) during repository sync
        yield Operation(OperationType.UPDATE, Repository, self.data.gh_repository)


class HookEventCreateAction(LoadAction):
    """Create the webhook event in a GitHub repository."""

    name = "gh-hook-event-create"
    data_cls = HookData

    def _generate_rows(self, **kwargs):
        """Generates rows for the second phase of enabling a gh repo webhook."""
        assert self.data.webhook_event
        if self.data.oauth_token:
            yield Operation(OperationType.UPDATE, ServerToken, self.data.oauth_token)
        yield Operation(OperationType.INSERT, WebhookEvent, self.data.webhook_event)


class HookEventUpdateAction(LoadAction):
    """Update the webhook event."""

    name = "gh-hook-event-update"
    data_cls = HookData

    def _generate_rows(self, **kwargs):
        """Generates rows for a webhook event update."""
        assert self.data.webhook_event
        yield Operation(OperationType.UPDATE, WebhookEvent, self.data.webhook_event)
