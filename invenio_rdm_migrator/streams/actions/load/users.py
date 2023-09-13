# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User actions module."""

from dataclasses import dataclass
from typing import Optional

from ....actions import LoadAction, LoadData
from ....load.postgresql.transactions.operations import Operation, OperationType
from ...models.users import LoginInformation, SessionActivity, User

# GLOBAL FIXME: partial updates would allow to remove the encrypt mixin from many of the
# actions, since only user registration and edit (with password change should) do the
# re-encryption. Would save time too.


@dataclass
class UserData(LoadData):
    """User action data."""

    user: dict
    login_information: Optional[dict] = None
    sessions: Optional[list] = None


class UserRegistrationAction(LoadAction):
    """Registers a user."""

    name = "register-user"
    data_cls = UserData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new user."""
        yield Operation(OperationType.INSERT, User, self.data.user)

        if self.data.login_information:
            yield Operation(
                OperationType.INSERT,
                LoginInformation,
                dict(user_id=self.data.user["id"], **self.data.login_information),
            )


# Handles many types of changes:
# - Profile change (email, username, full name)
# - Password change (including re-encryption)
# - User confirmation
# - User deactivation
class UserEditAction(LoadAction):
    """Registers a user."""

    name = "edit-user"
    data_cls = UserData

    def _generate_rows(self, **kwargs):
        """Generates rows for a user edit."""
        yield Operation(OperationType.UPDATE, User, self.data.user)

        if self.data.login_information:
            yield Operation(
                OperationType.UPDATE,
                LoginInformation,
                dict(user_id=self.data.user["id"], **self.data.login_information),
            )


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


class UserDeactivationAction(LoadAction):
    """Deactivate a user.

    For example, flag it as spam.
    """

    name = "deactivate-user"
    data_cls = UserData

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        assert not self.data.user["active"]

        yield Operation(OperationType.UPDATE, User, self.data.user)

        if self.data.login_information:
            yield Operation(
                OperationType.UPDATE,
                LoginInformation,
                dict(user_id=self.data.user["id"], **self.data.login_information),
            )

        for session in self.data.sessions:
            yield Operation(OperationType.DELETE, SessionActivity, session)
