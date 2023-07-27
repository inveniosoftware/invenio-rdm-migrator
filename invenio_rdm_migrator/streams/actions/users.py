# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User actions module."""

from ...actions import LoadAction

# from ..models.users import LoginInformation, User, UserIdentity


class UserRegistrationAction(LoadAction):
    """Registers a user."""

    name = "register-user"

    def __init__(
        self,
        tx_id,
        user,
        profile,
    ):
        """Constructor."""
        super().__init__(tx_id)
        assert user and profile  # i.e. not None as parameter
        self.user = user
        self.profile = profile

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        # login_info = self.user["user"].pop("login_information", None)
        # self.user["profile"] = self.profile

        # yield User(**self.user)

        # if login_info:
        #     yield LoginInformation(
        #         user_id=self.user["id"],
        #         **login_info,
        #     )
        # identities = data.get("identities", [])
        # for identity in identities:
        #     yield UserIdentity(
        #         id_user=self.user["id"],
        #         **identity,
        #     )
        pass


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
