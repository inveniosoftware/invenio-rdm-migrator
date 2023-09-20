# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GitHub actions tests."""

import pytest

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import (
    HookEventCreateAction,
    HookEventUpdateAction,
    HookRepoUpdateAction,
)
from invenio_rdm_migrator.streams.models.github import Repository, WebhookEvent
from invenio_rdm_migrator.streams.models.oauth import ServerToken


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


@pytest.fixture(scope="function")
def gh_repo_data():
    """GitHub repository data."""
    return {
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
        "id": "0d1b629d-7992-4650-b0b0-8908a0322bca",
        "github_id": 427018972,
        "name": "ppanero/zenodo-release-test",
        # the following None means the hook was removed, but it does not affect the tests
        "user_id": None,
        "hook": None,
        # note: ping was removed
    }


@pytest.fixture(scope="function")
def event_data():
    """Webhook event data."""
    return {
        "created": "2022-01-01T00:00:00",
        "updated": "2022-01-01T00:00:00",
        "id": "189d88dd-22d9-40d1-b3af-9da4b2bc4870",
        "receiver_id": "github",
        "user_id": 86490,
        "payload": '{"action": "published", "release": {"body": "Zenodo testing migration", "assets_url": "https://api.github.com/repos/ppanero/zenodo-release-test/releases/121854239/assets", "name": "more and more", "published_at": "2023-09-20T11:52:47Z", "author": {"following_url": "https://api.github.com/users/ppanero/following{/other_user}", "events_url": "https://api.github.com/users/ppanero/events{/privacy}", "avatar_url": "https://avatars.githubusercontent.com/u/6756943?v=4", "url": "https://api.github.com/users/ppanero", "gists_url": "https://api.github.com/users/ppanero/gists{/gist_id}", "html_url": "https://github.com/ppanero", "subscriptions_url": "https://api.github.com/users/ppanero/subscriptions", "node_id": "MDQ6VXNlcjY3NTY5NDM=", "repos_url": "https://api.github.com/users/ppanero/repos", "received_events_url": "https://api.github.com/users/ppanero/received_events", "gravatar_id": "", "starred_url": "https://api.github.com/users/ppanero/starred{/owner}{/repo}", "site_admin": false, "login": "ppanero", "type": "User", "id": 6756943, "followers_url": "https://api.github.com/users/ppanero/followers", "organizations_url": "https://api.github.com/users/ppanero/orgs"}, "url": "https://api.github.com/repos/ppanero/zenodo-release-test/releases/121854239", "created_at": "2023-09-20T11:50:17Z", "target_commitish": "main", "tarball_url": "https://api.github.com/repos/ppanero/zenodo-release-test/tarball/v4", "html_url": "https://github.com/ppanero/zenodo-release-test/releases/tag/v4", "zipball_url": "https://api.github.com/repos/ppanero/zenodo-release-test/zipball/v4", "tag_name": "v4", "node_id": "RE_kwDOGXPK3M4HQ1kf", "draft": false, "prerelease": false, "upload_url": "https://uploads.github.com/repos/ppanero/zenodo-release-test/releases/121854239/assets{?name,label}", "id": 121854239, "assets": []}, "sender": {"following_url": "https://api.github.com/users/ppanero/following{/other_user}", "events_url": "https://api.github.com/users/ppanero/events{/privacy}", "avatar_url": "https://avatars.githubusercontent.com/u/6756943?v=4", "url": "https://api.github.com/users/ppanero", "gists_url": "https://api.github.com/users/ppanero/gists{/gist_id}", "html_url": "https://github.com/ppanero", "subscriptions_url": "https://api.github.com/users/ppanero/subscriptions", "node_id": "MDQ6VXNlcjY3NTY5NDM=", "repos_url": "https://api.github.com/users/ppanero/repos", "received_events_url": "https://api.github.com/users/ppanero/received_events", "gravatar_id": "", "starred_url": "https://api.github.com/users/ppanero/starred{/owner}{/repo}", "site_admin": false, "login": "ppanero", "type": "User", "id": 6756943, "followers_url": "https://api.github.com/users/ppanero/followers", "organizations_url": "https://api.github.com/users/ppanero/orgs"}, "repository": {"issues_url": "https://api.github.com/repos/ppanero/zenodo-release-test/issues{/number}", "deployments_url": "https://api.github.com/repos/ppanero/zenodo-release-test/deployments", "stargazers_count": 0, "forks_url": "https://api.github.com/repos/ppanero/zenodo-release-test/forks", "mirror_url": null, "allow_forking": true, "subscription_url": "https://api.github.com/repos/ppanero/zenodo-release-test/subscription", "topics": [], "notifications_url": "https://api.github.com/repos/ppanero/zenodo-release-test/notifications{?since,all,participating}", "collaborators_url": "https://api.github.com/repos/ppanero/zenodo-release-test/collaborators{/collaborator}", "updated_at": "2021-12-02T13:03:26Z", "private": false, "pulls_url": "https://api.github.com/repos/ppanero/zenodo-release-test/pulls{/number}", "disabled": false, "issue_comment_url": "https://api.github.com/repos/ppanero/zenodo-release-test/issues/comments{/number}", "labels_url": "https://api.github.com/repos/ppanero/zenodo-release-test/labels{/name}", "has_wiki": true, "full_name": "ppanero/zenodo-release-test", "owner": {"following_url": "https://api.github.com/users/ppanero/following{/other_user}", "events_url": "https://api.github.com/users/ppanero/events{/privacy}", "avatar_url": "https://avatars.githubusercontent.com/u/6756943?v=4", "url": "https://api.github.com/users/ppanero", "gists_url": "https://api.github.com/users/ppanero/gists{/gist_id}", "html_url": "https://github.com/ppanero", "subscriptions_url": "https://api.github.com/users/ppanero/subscriptions", "node_id": "MDQ6VXNlcjY3NTY5NDM=", "repos_url": "https://api.github.com/users/ppanero/repos", "received_events_url": "https://api.github.com/users/ppanero/received_events", "gravatar_id": "", "starred_url": "https://api.github.com/users/ppanero/starred{/owner}{/repo}", "site_admin": false, "login": "ppanero", "type": "User", "id": 6756943, "followers_url": "https://api.github.com/users/ppanero/followers", "organizations_url": "https://api.github.com/users/ppanero/orgs"}, "statuses_url": "https://api.github.com/repos/ppanero/zenodo-release-test/statuses/{sha}", "id": 427018972, "keys_url": "https://api.github.com/repos/ppanero/zenodo-release-test/keys{/key_id}", "description": null, "tags_url": "https://api.github.com/repos/ppanero/zenodo-release-test/tags", "archived": false, "downloads_url": "https://api.github.com/repos/ppanero/zenodo-release-test/downloads", "assignees_url": "https://api.github.com/repos/ppanero/zenodo-release-test/assignees{/user}", "watchers": 0, "contents_url": "https://api.github.com/repos/ppanero/zenodo-release-test/contents/{+path}", "has_pages": false, "git_refs_url": "https://api.github.com/repos/ppanero/zenodo-release-test/git/refs{/sha}", "has_discussions": false, "has_projects": true, "clone_url": "https://github.com/ppanero/zenodo-release-test.git", "watchers_count": 0, "git_tags_url": "https://api.github.com/repos/ppanero/zenodo-release-test/git/tags{/sha}", "milestones_url": "https://api.github.com/repos/ppanero/zenodo-release-test/milestones{/number}", "languages_url": "https://api.github.com/repos/ppanero/zenodo-release-test/languages", "size": 8, "homepage": null, "fork": false, "commits_url": "https://api.github.com/repos/ppanero/zenodo-release-test/commits{/sha}", "releases_url": "https://api.github.com/repos/ppanero/zenodo-release-test/releases{/id}", "issue_events_url": "https://api.github.com/repos/ppanero/zenodo-release-test/issues/events{/number}", "archive_url": "https://api.github.com/repos/ppanero/zenodo-release-test/{archive_format}{/ref}", "comments_url": "https://api.github.com/repos/ppanero/zenodo-release-test/comments{/number}", "events_url": "https://api.github.com/repos/ppanero/zenodo-release-test/events", "contributors_url": "https://api.github.com/repos/ppanero/zenodo-release-test/contributors", "html_url": "https://github.com/ppanero/zenodo-release-test", "visibility": "public", "forks": 0, "compare_url": "https://api.github.com/repos/ppanero/zenodo-release-test/compare/{base}...{head}", "open_issues": 0, "node_id": "R_kgDOGXPK3A", "git_url": "git://github.com/ppanero/zenodo-release-test.git", "svn_url": "https://github.com/ppanero/zenodo-release-test", "merges_url": "https://api.github.com/repos/ppanero/zenodo-release-test/merges", "has_issues": true, "ssh_url": "git@github.com:ppanero/zenodo-release-test.git", "blobs_url": "https://api.github.com/repos/ppanero/zenodo-release-test/git/blobs{/sha}", "git_commits_url": "https://api.github.com/repos/ppanero/zenodo-release-test/git/commits{/sha}", "hooks_url": "https://api.github.com/repos/ppanero/zenodo-release-test/hooks", "has_downloads": true, "license": {"spdx_id": "MPL-2.0", "url": "https://api.github.com/licenses/mpl-2.0", "node_id": "MDc6TGljZW5zZTE0", "name": "Mozilla Public License 2.0", "key": "mpl-2.0"}, "name": "zenodo-release-test", "language": null, "url": "https://api.github.com/repos/ppanero/zenodo-release-test", "created_at": "2021-11-11T13:53:02Z", "open_issues_count": 0, "is_template": false, "pushed_at": "2023-09-20T11:50:38Z", "web_commit_signoff_required": false, "forks_count": 0, "default_branch": "main", "teams_url": "https://api.github.com/repos/ppanero/zenodo-release-test/teams", "trees_url": "https://api.github.com/repos/ppanero/zenodo-release-test/git/trees{/sha}", "branches_url": "https://api.github.com/repos/ppanero/zenodo-release-test/branches{/branch}", "subscribers_url": "https://api.github.com/repos/ppanero/zenodo-release-test/subscribers", "stargazers_url": "https://api.github.com/repos/ppanero/zenodo-release-test/stargazers"}}',
        "payload_headers": None,
        "response": '{"status": 409, "message": "The release has already been received."}',
        "response_headers": None,
        "response_code": 409,
    }


def test_github_repo_update(gh_repo_data):
    data = dict(tx_id=1, gh_repository=gh_repo_data)
    action = HookRepoUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == Repository


def test_github_hook_event_create_wo_token(event_data):
    data = dict(tx_id=1, webhook_event=event_data)
    action = HookEventCreateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.INSERT
    assert rows[0].model == WebhookEvent


def test_github_hook_event_create_w_token(event_data, oauth_token_data):
    data = dict(tx_id=1, webhook_event=event_data, oauth_token=oauth_token_data)
    action = HookEventCreateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 2
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == ServerToken
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == WebhookEvent


def test_github_hook_event_update(event_data):
    data = dict(tx_id=1, webhook_event=event_data)
    action = HookEventUpdateAction(data)
    rows = list(action.prepare())

    assert len(rows) == 1
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == WebhookEvent
