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
    OAuthGHDisconnectToken,
    OAuthLinkedAccountConnectAction,
    OAuthLinkedAccountDisconnectAction,
    OAuthServerTokenCreateAction,
    OAuthServerTokenDeleteAction,
    OAuthServerTokenUpdateAction,
)
from invenio_rdm_migrator.streams.models.oauth import (
    RemoteAccount,
    RemoteToken,
    ServerClient,
    ServerToken,
)
from invenio_rdm_migrator.streams.models.users import UserIdentity


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


def test_create_oauth_server_token(session, oauth_client_data, oauth_token_data):
    data = dict(
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenCreateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 2
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == ServerClient
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == ServerToken


def test_client_oauth_server_token(session, oauth_client_data, oauth_token_data):
    data = dict(
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient
    assert rows[1].type == OperationType.UPDATE
    assert rows[1].model == ServerToken


def test_client_oauth_server_token_only_client(session, oauth_client_data):
    data = dict(
        client=oauth_client_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient


def test_client_oauth_server_token_only_server(session, oauth_token_data):
    data = dict(
        token=oauth_token_data,
    )
    action = OAuthServerTokenUpdateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerToken


def test_delete_oauth_server_token(session, oauth_client_data, oauth_token_data):
    data = dict(
        token=oauth_token_data,
    )
    action = OAuthServerTokenDeleteAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == ServerToken


def test_delete_oauth_server_token_w_client(
    session, oauth_client_data, oauth_token_data
):
    data = dict(
        client=oauth_client_data,
        token=oauth_token_data,
    )
    action = OAuthServerTokenDeleteAction(data)
    with pytest.raises(AssertionError):
        list(action.prepare(session))


def test_create_oauth_application(session, oauth_client_data):
    data = dict(
        client=oauth_client_data,
    )
    action = OAuthApplicationCreateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == ServerClient


def test_update_oauth_application(session, oauth_client_data):
    data = dict(
        client=oauth_client_data,
    )
    action = OAuthApplicationUpdateAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerClient


def test_delete_oauth_application(session, oauth_client_data):
    data = dict(
        client=oauth_client_data,
    )
    action = OAuthApplicationDeleteAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 1
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == ServerClient


###
# OAuth Client
###


@pytest.fixture(scope="function")
def oauth_remote_account():
    """OAuth client remote account."""
    return {
        "id": 8546,
        "user_id": 22858,
        "client_id": "APP-MAX7XCD8Q98X4VT6",
        "extra_data": '{"orcid": "0000-0002-5676-5956", "full_name": "Alex Ioannidis"}',
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
    }


@pytest.fixture(scope="function")
def oauth_remote_token():
    """OAuth client remote token."""
    return {
        "id_remote_account": 8546,
        "token_type": "",
        "access_token": "R3RVeGc3K0RrM25rbXc4ZWxGM3oxYVA4LzcwVWpCNkM4aG8vRy9CNWxkZFFCMk9OR1d2d29lN3dKdWk2eEVTQQ==",
        "secret": "",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
    }


@pytest.fixture(scope="function")
def account_user_identity():
    """OAuth client user identity."""
    return {
        "id": "0000-0002-5676-5956",
        "method": "orcid",
        "id_user": 22858,
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
    }


def test_connect_minimal_oauth_account(
    session,
    oauth_remote_account,
    oauth_remote_token,
    account_user_identity,
):
    data = dict(
        remote_account=oauth_remote_account,
        remote_token=oauth_remote_token,
        user_identity=account_user_identity,
    )
    action = OAuthLinkedAccountConnectAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 3
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == RemoteAccount
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == RemoteToken
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == UserIdentity


def test_connect_full_oauth_account(
    session,
    oauth_remote_account,
    oauth_remote_token,
    account_user_identity,
    oauth_client_data,
    oauth_token_data,
):
    data = dict(
        remote_account=oauth_remote_account,
        remote_token=oauth_remote_token,
        user_identity=account_user_identity,
        server_client=oauth_client_data,
        server_token=oauth_token_data,
    )
    action = OAuthLinkedAccountConnectAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 5
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == RemoteAccount
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == RemoteToken
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == UserIdentity
    assert rows[3].type == OperationType.INSERT
    assert rows[3].model == ServerClient
    assert rows[4].type == OperationType.INSERT
    assert rows[4].model == ServerToken


def test_disconnect_oauth_account(
    session,
    oauth_remote_account,
    oauth_remote_token,
    account_user_identity,
):
    data = dict(
        remote_account=oauth_remote_account,
        remote_token=oauth_remote_token,
        user_identity=account_user_identity,
    )
    action = OAuthLinkedAccountDisconnectAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 3
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == UserIdentity
    assert rows[1].type == OperationType.DELETE
    assert rows[1].model == RemoteToken
    assert rows[2].type == OperationType.DELETE
    assert rows[2].model == RemoteAccount


def test_disconnect_gh_oauth_account(session, oauth_token_data, account_user_identity):
    data = dict(
        token=oauth_token_data,
        user_identity=account_user_identity,
    )
    action = OAuthGHDisconnectToken(data)
    rows = list(action.prepare(session))

    assert len(rows) == 2
    assert rows[0].type == OperationType.DELETE
    assert rows[0].model == UserIdentity
    assert rows[1].type == OperationType.DELETE
    assert rows[1].model == ServerToken
