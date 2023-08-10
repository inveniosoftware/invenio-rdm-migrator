# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import (
    UserDeactivationAction,
    UserEditAction,
    UserRegistrationAction,
)
from invenio_rdm_migrator.streams.models.users import (
    LoginInformation,
    SessionActivity,
    User,
)


@pytest.fixture(scope="function")
def user_data():
    return {
        "id": 123456,
        "created": "2021-05-01T00:00:00",
        "updated": "2021-05-01T00:00:00",
        "username": "test_user",
        "displayname": "test_user",
        "email": "someaddr@domain.org",
        "password": "zmkNzdnG1PXP5C3dmZqlJw==",
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


@pytest.fixture()
def sessions_data():
    return [
        {
            "user_id": None,
            "created": 0,
            "updated": 0,
            "sid_s": "bc51d8ea3ccc285c_64cb64fa",
            "ip": None,
            "country": None,
            "browser": None,
            "browser_version": None,
            "os": None,
            "device": None,
        },
        {
            "user_id": None,
            "created": 0,
            "updated": 0,
            "sid_s": "754493997337aa0a_64cb65bc",
            "ip": None,
            "country": None,
            "browser": None,
            "browser_version": None,
            "os": None,
            "device": None,
        },
    ]


def test_register_new_user(secret_keys_state, user_data, login_info_data):
    data = dict(tx_id=1, user=user_data, login_information=login_info_data)
    action = UserRegistrationAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == User
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == LoginInformation


def test_edit_user(secret_keys_state, user_data, login_info_data):
    data = dict(tx_id=1, user=user_data, login_information=login_info_data)
    action = UserEditAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == User
    assert rows[1].type == OperationType.UPDATE
    assert rows[1].model == LoginInformation


def test_deactivate_user(secret_keys_state, user_data, sessions_data):
    # prepare
    user_data["active"] = False

    # test
    data = dict(tx_id=1, user=user_data, sessions=sessions_data)
    action = UserDeactivationAction(data)
    rows = list(action.prepare())
    assert len(rows) == 3
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == User
    assert rows[1].type == OperationType.DELETE
    assert rows[1].model == SessionActivity
    assert rows[2].type == OperationType.DELETE
    assert rows[2].model == SessionActivity
