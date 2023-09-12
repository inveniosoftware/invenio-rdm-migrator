# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community actions tests."""

import pytest

from invenio_rdm_migrator.load.ids import generate_uuid
from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import (
    CommunityCreateAction,
    CommunityDeleteAction,
    CommunityUpdateAction,
)
from invenio_rdm_migrator.streams.models.communities import (
    Community,
    CommunityFile,
    CommunityMember,
)
from invenio_rdm_migrator.streams.models.files import (
    FilesBucket,
    FilesInstance,
    FilesObjectVersion,
)
from invenio_rdm_migrator.streams.models.oai import OAISet


@pytest.fixture(scope="function")
def community_data():
    """Community data."""
    return {
        "slug": "test-community",
        "created": "2021-05-01T00:00:00",
        "updated": "2021-05-01T00:00:00",
        "json": {
            "files": {"enabled": True},
            "access": {
                "visibility": "public",
                "member_policy": "open",
                "record_policy": "open",
            },
            "metadata": {
                "page": "<p>This is the community page</p>",
                "title": "Test community",
                "description": "Test community description",
                "curation_policy": "<p>Curation policy for test community</p>",
            },
        },
        "version_id": 1,
    }


@pytest.fixture()
def owner_data():
    """Community owner data."""
    return {
        "created": "2021-05-01T00:00:00",
        "updated": "2021-05-01T00:00:00",
        "json": {},
        "version_id": 1,
        "role": "owner",
        "visible": True,
        "active": True,
        "user_id": 1234,
        "group_id": None,
        "request_id": None,
    }


@pytest.fixture(scope="function")
def oai_set_data():
    """OAI set data."""
    return {
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "spec": "community-test-community",
        "name": "Test community",
        "description": "Test community description",
    }


@pytest.fixture(scope="function")
def bucket_data():
    """Bucket data."""
    return {
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "default_location": 1,
        "default_storage_class": "S",
        "size": 1562554,
        "quota_size": 50000000000,
        "max_file_size": 50000000000,
        "locked": False,
        "deleted": False,
    }


@pytest.fixture(scope="function")
def fi_data():
    """File instance data."""
    return {
        "id": "e94b243e-9c0c-44df-bd1f-6decc374cf78",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "uri": "root://eosmedia.cern.ch//eos/media/zenodo/test/data/e9/4b/243e-9c0c-44df-bd1f-6decc374cf78/data",
        "storage_class": "S",
        "size": 1562554,
        "checksum": "md5:3cc016be06f2be46d3a438db23c40bf3",
        "readable": True,
        "writable": False,
        "last_check_at": None,
        "last_check": True,
    }


@pytest.fixture(scope="function")
def ov_data(fi_data):
    """Object version data."""
    return {
        "version_id": "f8200dc7-55b6-4785-abd0-f3d13b143c98",
        "created": "2023-06-29T13:00:00",
        "updated": "2023-06-29T14:00:00",
        "key": "logo",
        "bucket_id": "<other_bucket>",
        "file_id": fi_data["id"],
        "_mimetype": None,
        "is_head": True,
    }


@pytest.fixture(scope="function")
def community_file_data():
    """Community file data."""
    return {
        "json": {},
        "record_id": None,
        "version_id": 1,
        "key": "logo",
    }


def test_create_community(
    communities_state,
    community_data,
    owner_data,
    oai_set_data,
    bucket_data,
    fi_data,
    ov_data,
    community_file_data,
):
    """Test community create action."""
    data = dict(
        tx_id=1,
        community=community_data,
        owner=owner_data,
        bucket=bucket_data,
        oai_set=oai_set_data,
        community_file=community_file_data,
        file_instance=fi_data,
        object_version=ov_data,
    )

    action = CommunityCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 7

    bucket_row, community_row, oai_set_row, owner_row, fi_row, ov_row, cf_row = rows

    bucket_id = bucket_row.data["id"]
    assert bucket_row.type == OperationType.INSERT
    assert bucket_row.model == FilesBucket

    c_id = community_row.data["id"]
    slug = community_row.data["slug"]
    assert community_row.type == OperationType.INSERT
    assert community_row.model == Community
    assert community_row.data["bucket_id"] == bucket_id

    oai_set_id = oai_set_row.data["id"]
    assert oai_set_row.type == OperationType.INSERT
    assert oai_set_row.model == OAISet
    assert oai_set_id
    assert oai_set_row.data["search_pattern"] == f"parent.communities.ids:{c_id}"
    assert oai_set_row.data["system_created"] is True

    assert owner_row.type == OperationType.INSERT
    assert owner_row.model == CommunityMember
    assert owner_row.data["community_id"] == c_id

    assert fi_row.type == OperationType.INSERT
    assert fi_row.model == FilesInstance

    ov_id = ov_row.data["version_id"]
    assert ov_row.type == OperationType.INSERT
    assert ov_row.model == FilesObjectVersion
    assert ov_row.data["bucket_id"] == bucket_id

    cf_id = cf_row.data["id"]
    assert cf_row.type == OperationType.INSERT
    assert cf_row.model == CommunityFile
    assert cf_row.data["record_id"] == c_id
    assert cf_row.data["object_version_id"] == ov_id

    # Community is in the state
    assert communities_state.get(slug) == {
        "slug": slug,
        "id": c_id,
        "bucket_id": bucket_id,
        "oai_set_id": oai_set_id,
        "community_file_id": cf_id,
        "logo_object_version_id": ov_id,
    }


def test_create_community_no_logo(
    communities_state,
    community_data,
    owner_data,
    oai_set_data,
    bucket_data,
):
    """Test community create action w/o logo."""
    data = dict(
        tx_id=1,
        community=community_data,
        owner=owner_data,
        bucket=bucket_data,
        oai_set=oai_set_data,
    )

    action = CommunityCreateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 4

    bucket_row, community_row, oai_set_row, owner_row = rows

    bucket_id = bucket_row.data["id"]
    assert bucket_row.type == OperationType.INSERT
    assert bucket_row.model == FilesBucket

    c_id = community_row.data["id"]
    assert community_row.type == OperationType.INSERT
    assert community_row.model == Community
    assert community_row.data["bucket_id"] == bucket_id

    assert oai_set_row.type == OperationType.INSERT
    assert oai_set_row.model == OAISet
    assert oai_set_row.data["id"]
    assert oai_set_row.data["search_pattern"] == f"parent.communities.ids:{c_id}"
    assert oai_set_row.data["system_created"] is True

    assert owner_row.type == OperationType.INSERT
    assert owner_row.model == CommunityMember
    assert owner_row.data["community_id"] == c_id

    # Community is in the state
    assert communities_state.get(community_row.data["slug"]) == {
        "slug": community_row.data["slug"],
        "id": c_id,
        "bucket_id": bucket_id,
        "oai_set_id": oai_set_row.data["id"],
        "community_file_id": None,
        "logo_object_version_id": None,
    }


def test_update_community(
    communities_state,
    community_data,
    fi_data,
    ov_data,
    community_file_data,
):
    """Test community update action."""
    # Use a community that's already in the state
    slug = community_data["slug"] = "comm"
    state = communities_state.get(slug)
    community_id = state["id"]
    bucket_id = state["bucket_id"]
    oai_set_id = state["oai_set_id"]

    # remove/modify some keys from the community
    community_data.pop("created")
    community_data.pop("version_id")
    community_data["json"]["metadata"]["title"] = "Test community (v2)"

    data = dict(
        tx_id=1,
        community=community_data,
        community_file=community_file_data,
        file_instance=fi_data,
        object_version=ov_data,
    )
    action = CommunityUpdateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 4

    community_row, fi_row, ov_row, cf_row = rows

    assert community_row.type == OperationType.UPDATE
    assert community_row.model == Community
    assert community_row.data["id"] == community_id
    # Only the PK and the updated values ae present
    assert community_row.data.keys() == {"id", "updated", "json", "slug"}

    assert fi_row.type == OperationType.INSERT
    assert fi_row.model == FilesInstance

    ov_id = ov_row.data["version_id"]
    assert ov_row.type == OperationType.INSERT
    assert ov_row.model == FilesObjectVersion
    assert ov_row.data["bucket_id"] == bucket_id

    cf_id = cf_row.data["id"]
    assert cf_row.type == OperationType.INSERT
    assert cf_row.model == CommunityFile
    assert cf_row.data["record_id"] == community_id
    assert cf_row.data["object_version_id"] == ov_id

    # Community state has been updated with the file PKs
    assert communities_state.get(slug) == {
        "slug": slug,
        "id": community_id,
        "bucket_id": bucket_id,
        "oai_set_id": oai_set_id,
        "community_file_id": cf_id,
        "logo_object_version_id": ov_id,
    }


def test_update_community_only_metadata(
    communities_state,
    community_data,
):
    """Test community update action for only metadata."""
    # Use a community that's already in the state
    slug = community_data["slug"] = "comm"
    state = communities_state.get(slug)
    community_id = state["id"]
    bucket_id = state["bucket_id"]
    oai_set_id = state["oai_set_id"]

    # remove/modify some keys from the community
    community_data.pop("created")
    community_data.pop("version_id")
    community_data["json"]["metadata"]["title"] = "Test community (v2)"

    data = dict(tx_id=1, community=community_data)
    action = CommunityUpdateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 1

    (community_row,) = rows

    assert community_row.type == OperationType.UPDATE
    assert community_row.model == Community
    assert community_row.data["id"] == community_id
    assert community_row.data.keys() == {"id", "updated", "json", "slug"}

    # Community state has been updated with the file PKs
    assert communities_state.get(slug) == {
        "slug": slug,
        "id": community_id,
        "bucket_id": bucket_id,
        "oai_set_id": oai_set_id,
        "community_file_id": None,
        "logo_object_version_id": None,
    }


def test_update_community_update_existing_logo(
    communities_state,
    community_data,
    fi_data,
    ov_data,
    community_file_data,
):
    """Test community update action for a community with an existing logo."""
    # Use a community that's already in the state
    slug = community_data["slug"] = "comm"
    state = communities_state.get(slug)
    community_id = state["id"]
    bucket_id = state["bucket_id"]
    oai_set_id = state["oai_set_id"]

    # Add existing logo file PKs
    community_file_id = generate_uuid(None)
    old_logo_object_version_id = generate_uuid(None)
    communities_state.update(
        slug,
        {
            "community_file_id": community_file_id,
            "logo_object_version_id": old_logo_object_version_id,
        },
    )

    data = dict(
        tx_id=1,
        community=community_data,
        community_file=community_file_data,
        file_instance=fi_data,
        object_version=ov_data,
    )
    action = CommunityUpdateAction(data)
    rows = list(action.prepare())
    assert len(rows) == 5

    community_row, fi_row, old_ov_row, new_ov_row, cf_row = rows

    assert community_row.type == OperationType.UPDATE
    assert community_row.model == Community
    assert community_row.data["id"] == community_id

    assert fi_row.type == OperationType.INSERT
    assert fi_row.model == FilesInstance

    old_ov_row.data["version_id"] == old_logo_object_version_id
    assert old_ov_row.type == OperationType.UPDATE
    assert old_ov_row.model == FilesObjectVersion
    assert old_ov_row.data["is_head"] is False

    new_ov_id = new_ov_row.data["version_id"]
    assert new_ov_id != old_logo_object_version_id
    assert new_ov_row.type == OperationType.INSERT
    assert new_ov_row.model == FilesObjectVersion
    assert new_ov_row.data["bucket_id"] == bucket_id

    assert cf_row.data["id"] == community_file_id
    assert cf_row.type == OperationType.UPDATE
    assert cf_row.model == CommunityFile
    assert cf_row.data["record_id"] == community_id
    assert cf_row.data["object_version_id"] == new_ov_id

    # Community state has been updated with the file PKs
    assert communities_state.get(slug) == {
        "slug": slug,
        "id": community_id,
        "bucket_id": bucket_id,
        "oai_set_id": oai_set_id,
        "community_file_id": community_file_id,
        "logo_object_version_id": new_ov_id,
    }


def test_delete_community(
    communities_state,
    community_data,
):
    """Test community delete action."""
    # Use a community that's already in the state
    slug = community_data["slug"] = "comm"
    state = communities_state.get(slug)
    community_id = state["id"]
    oai_set_id = state["oai_set_id"]

    data = dict(tx_id=1, community=community_data)
    action = CommunityDeleteAction(data)
    rows = list(action.prepare())
    assert len(rows) == 2

    community_row, oai_set_row = rows

    assert community_row.type == OperationType.UPDATE
    assert community_row.model == Community
    assert community_row.data["id"] == community_id
    assert community_row.data["json"] is None

    assert oai_set_row.type == OperationType.DELETE
    assert oai_set_row.model == OAISet
    assert oai_set_row.data["id"] == oai_set_id

    # Community state is not deleted
    assert communities_state.get(slug)


def test_delete_community_with_logo(
    communities_state,
    community_data,
):
    """Test community delete action for community with logo."""
    # Use a community that's already in the state
    slug = community_data["slug"] = "comm"
    state = communities_state.get(slug)
    community_id = state["id"]
    oai_set_id = state["oai_set_id"]

    # Add existing logo file PKs
    community_file_id = generate_uuid(None)
    logo_object_version_id = generate_uuid(None)
    communities_state.update(
        slug,
        {
            "community_file_id": community_file_id,
            "logo_object_version_id": logo_object_version_id,
        },
    )

    data = dict(tx_id=1, community=community_data)
    action = CommunityDeleteAction(data)
    rows = list(action.prepare())
    assert len(rows) == 4

    community_row, oai_set_row, ov_row, cf_row = rows

    assert community_row.type == OperationType.UPDATE
    assert community_row.model == Community
    assert community_row.data["id"] == community_id
    assert community_row.data["json"] is None

    assert oai_set_row.type == OperationType.DELETE
    assert oai_set_row.model == OAISet
    assert oai_set_row.data["id"] == oai_set_id

    assert ov_row.type == OperationType.DELETE
    assert ov_row.model == FilesObjectVersion
    assert ov_row.data["version_id"] == logo_object_version_id

    assert cf_row.type == OperationType.DELETE
    assert cf_row.model == CommunityFile
    assert cf_row.data["id"] == community_file_id

    # Community state is not deleted
    assert communities_state.get(slug)
