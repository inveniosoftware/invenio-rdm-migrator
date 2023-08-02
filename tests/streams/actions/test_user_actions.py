# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions import UserRegistrationAction
from invenio_rdm_migrator.streams.models.users import LoginInformation, User


@pytest.fixture()
def user_data():
    return {
        "id": 123456,
        "created": 1640995200000000,
        "updated": 1640995200000000,
        "username": "test_user",
        "displayname": "test_user",
        "email": "someaddr@domain.org",
        "password": "$pbkdf2-sha512$Th1sW0ulDB34P4sSw0rd",
        "active": True,
        "confirmed_at": None,
        "version_id": 1,
        "profile": {"full_name": "User test"},
        "preferences": {
            "visibility": "restricted",
            "email_visibility": "restricted",
        },
    }


@pytest.fixture()
def login_info_data():
    return {
        "last_login_at": None,
        "current_login_at": None,
        "last_login_ip": None,
        "current_login_ip": None,
        "login_count": None,
    }


def test_register_new_user(user_data, login_info_data):
    data = dict(tx_id=1, user=user_data, login_information=login_info_data)
    action = UserRegistrationAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2
    assert rows[0].type == OperationType.INSERT
    assert isinstance(rows[0].obj, User)
    assert rows[1].type == OperationType.INSERT
    assert isinstance(rows[1].obj, LoginInformation)
