# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import (
    OAuthApplicationCreateAction,
    OAuthApplicationDeleteAction,
    OAuthApplicationUpdateAction,
    OAuthServerTokenCreateAction,
    OAuthServerTokenDeleteAction,
    OAuthServerTokenUpdateAction,
)
from invenio_rdm_migrator.streams.models.oauth import ServerClient, ServerToken


@pytest.fixture(scope="function")
def oauth_client_data():
    """OAuth2Server client data."""

    return {
        "name": "test-incremental-token",
        "description": "",
        "website": "",
        "user_id": 123456,
        "client_id": "cH4ng3DZPeBjqj7uMB1JWXavhxebu6V0mwMtvMr",
        "client_secret": "cH4ng3D143BM6gKc29VN0rWZPI4wi0gHBcJQYdVNLtibTK0AR1ZWbWT5oYeQ",
        "is_confidential": False,
        "is_internal": True,
        "_redirect_uris": None,
        "_default_scopes": "tokens:generate user:email",
    }


@pytest.fixture(scope="function")
def oauth_token_data():
    """OAuth2Server token data."""

    return {
        "id": 156666,
        "client_id": "cH4ng3DZPeBjqj7uMB1JWXavhxebu6V0mwMtvMr",
        "user_id": 123456,
        "token_type": "bearer",
        "access_token": "cH4ng3DzbXd4QTcrRjFMcTVMRHl3QlY2Rkdib0VwREY4aDhPcHo2dUt2ZnZ3OVVPa1BvRDl0L1NRZmFrdXNIU2hJR2JWc0NHZDZSVEhVT2JQcmdjS1E9PQ==",
        "refresh_token": None,
        "expires": None,
        "_scopes": "tokens:generate user:email",
        "is_personal": True,
        "is_internal": False,
    }


def test_create_oauth_server_token(oauth_client_data, oauth_token_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenCreateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 2
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == ServerClient
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == ServerToken


def test_client_oauth_server_token(oauth_client_data, oauth_token_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient
    assert rows[1].type == OperationType.UPDATE
    assert rows[1].model == ServerToken


def test_client_oauth_server_token_only_client(oauth_client_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient


def test_client_oauth_server_token_only_server(oauth_token_data):
    data = dict(
        tx_id=1,
        token=oauth_token_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerToken


def test_delete_oauth_server_token(oauth_client_data, oauth_token_data):
    data = dict(
        tx_id=1,
        token=oauth_token_data,
    )
    action = OAuthServerTokenDeleteAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == ServerToken


def test_delete_oauth_server_token_w_client(oauth_client_data, oauth_token_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenDeleteAction(data)
    with pytest.raises(AssertionError):
        list(action.prepare())


def test_create_oauth_application(oauth_client_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
    )
    action = OAuthApplicationCreateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == ServerClient


def test_update_oauth_application(oauth_client_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
    )
    action = OAuthApplicationUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient


def test_delete_oauth_application(oauth_client_data):
    data = dict(
        tx_id=1,
        client=oauth_client_data,
    )
    action = OAuthApplicationDeleteAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == ServerClient
