# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User actions module."""

from dataclasses import dataclass

from ...actions import LoadAction, LoadData
from ...load.postgresql.transactions.operations import Operation, OperationType
from ..models.users import LoginInformation, User


@dataclass
class UserData(LoadData):
    """User action data."""

    user: dict
    login_information: dict


class UserRegistrationAction(LoadAction):
    """Registers a user."""

    name = "register-user"
    data_cls = UserData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new user."""
        # https://github.com/inveniosoftware/invenio-rdm-migrator/issues/123
        from datetime import datetime

        self.data.user["created"] = datetime.fromtimestamp(
            self.data.user["created"] / 1_000_000
        )
        self.data.user["updated"] = datetime.fromtimestamp(
            self.data.user["updated"] / 1_000_000
        )

        yield Operation(OperationType.INSERT, User(**self.data.user))

        if self.data.login_information:
            yield Operation(
                OperationType.INSERT,
                LoginInformation(
                    user_id=self.data.user["id"],
                    **self.data.login_information,
                ),
            )


# FIXME: To be verified
# an email confirmation would be a user update with a change on `confirmed_at`
# an email change would be a user update with a change on `email`
# an password change would be a user update with a change on `password`, requires re-encryption
class UserEditAction(LoadAction):
    """Registers a user."""

    name = "edit-user"

    def __init__(
        self,
        tx_id,
        user,
    ):
        """Constructor."""
        super().__init__(tx_id)
        assert user  # i.e. not None as parameter
        self.user = user

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        pass


class UserProfileEditAction(LoadAction):
    """Registers a user."""

    name = "edit-user-profile"

    def __init__(
        self,
        tx_id,
        profile,
    ):
        """Constructor."""
        super().__init__(tx_id)
        assert profile  # i.e. not None as parameter
        self.profile = profile

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        pass


# FIXME: do we want to migrate user sessions? might be a good idea to force log-in to get
# an idea of active users
