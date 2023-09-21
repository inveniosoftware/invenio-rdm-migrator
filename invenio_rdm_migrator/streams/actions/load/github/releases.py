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
from ....models.github import Release, Repository


@dataclass
class ReleaseData(LoadData):
    """GitHub release action data."""

    gh_release: dict
    gh_repository: Optional[dict] = None


class ReleaseReceiveAction(LoadAction):
    """Receive/Create a GitHub release action."""

    name = "gh-release-receive"
    data_cls = ReleaseData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        assert self.data.gh_repository
        yield Operation(OperationType.UPDATE, Repository, self.data.gh_repository)
        yield Operation(OperationType.INSERT, Release, self.data.gh_release)


class ReleaseUpdateAction(LoadAction):
    """Update a GitHub release action."""

    name = "gh-release-update"
    data_cls = ReleaseData

    def _generate_rows(self, **kwargs):
        """Generates rows for a gh repo update."""
        yield Operation(OperationType.UPDATE, Release, self.data.gh_release)
