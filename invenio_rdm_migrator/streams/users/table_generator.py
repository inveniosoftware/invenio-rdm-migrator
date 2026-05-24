# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration user table load module."""


from ...load.postgresql.bulk.generators import TableGenerator
from ..models.users import LoginInformation, User, UserIdentity


class UserTableGenerator(TableGenerator):
    """User and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                User,
                LoginInformation,
                UserIdentity,
            ],
        )

    def _generate_rows(self, data, **kwargs):
        user = data["user"]
        login_info = user.pop("login_information", None)
        yield User(**user)
        if login_info:
            yield LoginInformation(
                user_id=user["id"],
                **login_info,
            )
        identities = data.get("identities", [])
        for identity in identities:
            yield UserIdentity(
                id_user=user["id"],
                **identity,
            )
