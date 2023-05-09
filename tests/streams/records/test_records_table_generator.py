# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Records/Drafts table generator tests."""

from copy import deepcopy
from unittest.mock import patch

import pytest

from invenio_rdm_migrator.load.models import PersistentIdentifier
from invenio_rdm_migrator.streams.communities.models import RDMParentCommunityMetadata
from invenio_rdm_migrator.streams.records.load import (
    RDMDraftTableGenerator,
    RDMRecordTableGenerator,
)
from invenio_rdm_migrator.streams.records.models import (
    RDMDraftMetadata,
    RDMParentMetadata,
    RDMRecordMetadata,
)


class MockUTCDate:
    """Mock UTC date."""

    def isoformat(self):
        """ISO formatter datetime."""
        return "2023-04-01 12:00:00.00000"


class MockDateTime:
    """Mock datetime class."""

    def utcnow(self):
        """Nop func."""
        return MockUTCDate()


INIT_PID_PK = 10123
"""Initial value for PID primary key generation."""


@pytest.fixture(scope="function")
def restart_pid_pk():
    """Restart counter."""
    global INIT_PID_PK
    INIT_PID_PK = 10123


def mock_pid_pk():
    """Mock pid pk generation."""
    global INIT_PID_PK
    INIT_PID_PK += 1
    return str(INIT_PID_PK)


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_single_record_generate_rows(
    cache, restart_pid_pk, transformed_record_entry_pks
):
    """A published record with a non cached parent.

    It does not make sense to also test with a cached parent since that would mean
    there was a previous version of the record, which is tested separately in this module.
    """
    tg = RDMRecordTableGenerator(
        parents_cache=cache["parents"],
        records_cache=cache["records"],
        communities_cache=cache["communities"],
    )
    rows = list(tg._generate_rows(transformed_record_entry_pks))
    expected_rows = [
        RDMParentMetadata(  # parent record
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            json={
                "id": "12345677",
                "pid": {
                    "pk": "10122",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "R",
                },
                "communities": {
                    "ids": [
                        "12345678-abcd-1a2b-3c4d-123abc456def",
                        "12345678-abcd-1a2b-3c4d-123abc123abc",
                    ],
                    "default": "12345678-abcd-1a2b-3c4d-123abc456def",
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
        ),
        PersistentIdentifier(  # parent recid
            id="10122",
            pid_type="recid",
            pid_value="12345677",
            status="R",
            object_type="rec",
            object_uuid="12345678-abcd-1a2b-3c4d-123abc456def",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        RDMParentCommunityMetadata(  # parent community
            community_id="12345678-abcd-1a2b-3c4d-123abc456def",
            record_id="12345678-abcd-1a2b-3c4d-123abc456def",
            request_id=None,
        ),
        RDMRecordMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823386",
            json={
                "id": "12345678",
                "pid": {
                    "pk": "10123",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "R",
                },
                "pids": {
                    "oai": {
                        "provider": "oai",
                        "identifier": "oai:zenodo.org:12345678",
                    },
                    "doi": {
                        "client": "datacite",
                        "provider": "datacite",
                        "identifier": "10.5281/zenodo.12345678",
                    },
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
            index=1,
            bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
        ),
        PersistentIdentifier(  # recid
            id="10123",
            pid_type="recid",
            pid_value="12345678",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # doi
            id="10124",
            pid_type="doi",
            pid_value="10.5281/zenodo.12345678",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # oai
            id="10125",
            pid_type="oai",
            pid_value="oai:zenodo.org:12345678",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
    ]

    assert rows == expected_rows

    assert len(cache["parents"].all()) == 2  # pre-existing and new
    assert len(cache["records"].all()) == 1


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_single_draft_generate_rows(cache, restart_pid_pk, transformed_draft_entry_pks):
    """A new draft, not published."""
    tg = RDMDraftTableGenerator(
        parents_cache=cache["parents"],
        records_cache=cache["records"],
        communities_cache=cache["communities"],
    )
    rows = list(tg._generate_rows(transformed_draft_entry_pks))
    expected_rows = [
        RDMParentMetadata(  # parent record
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            json={
                "id": "12345677",
                "pid": {
                    "pk": "10122",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "N",
                },
                "communities": {
                    "ids": [
                        "12345678-abcd-1a2b-3c4d-123abc456def",
                        "12345678-abcd-1a2b-3c4d-123abc123abc",
                    ],
                    "default": "12345678-abcd-1a2b-3c4d-123abc456def",
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
        ),
        PersistentIdentifier(  # parent recid
            id="10122",
            pid_type="recid",
            pid_value="12345677",
            status="N",
            object_type="rec",
            object_uuid="12345678-abcd-1a2b-3c4d-123abc456def",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        RDMDraftMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823386",
            json={
                "id": "12345678",
                "pid": {
                    "pk": "10123",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "N",
                },
                "pids": {
                    "doi": {
                        "provider": "external",
                        "identifier": "10.1234/foo",
                    },
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
            index=1,
            bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=None,
        ),
        PersistentIdentifier(  # recid
            id="10123",
            pid_type="recid",
            pid_value="12345678",
            status="N",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
    ]

    assert rows == expected_rows

    assert len(cache["parents"].all()) == 2  # pre-existing and new
    assert len(cache["records"].all()) == 0


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_record_versions_and_old_draft_generate_rows(
    cache, restart_pid_pk, transformed_record_entry_pks, transformed_draft_entry_pks
):
    """A record with two versions (v1, v2) and a draft of the first version (v1)."""
    tgs = [
        RDMRecordTableGenerator(
            parents_cache=cache["parents"],
            records_cache=cache["records"],
            communities_cache=cache["communities"],
        ),
        RDMDraftTableGenerator(
            parents_cache=cache["parents"],
            records_cache=cache["records"],
            communities_cache=cache["communities"],
        ),
    ]

    v1 = transformed_record_entry_pks
    v2 = deepcopy(transformed_record_entry_pks)
    v2["record"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823387"
    v2["record"]["index"] = 2
    v2["record"]["json"]["id"] = "12345679"
    v2["record"]["json"]["pid"]["pk"] = "10126"  # pk, not pid value
    v2["record"]["json"]["pids"]["oai"]["identifier"] = "oai:zenodo.org:12345679"
    v2["record"]["json"]["pids"]["doi"]["identifier"] = "10.5281/zenodo.12345679"
    d_v1 = transformed_draft_entry_pks
    d_v1["draft"]["json"]["pid"]["pk"] = "10123"  # pk, not pid value, same as v1
    d_v1["draft"]["json"]["pid"][
        "status"
    ] = "R"  # same as already R pid form the record
    d_v1["draft"]["fork_version_id"] = 1

    rows = []
    for entry in [v1, v2, d_v1]:
        for tg in tgs:
            rows.extend(list(tg._generate_rows(entry)))

    expected_rows_v2 = [
        RDMRecordMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823387",
            json={
                "id": "12345679",
                "pid": {
                    "pk": "10126",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "R",
                },
                "pids": {
                    "oai": {
                        "provider": "oai",
                        "identifier": "oai:zenodo.org:12345679",
                    },
                    "doi": {
                        "client": "datacite",
                        "provider": "datacite",
                        "identifier": "10.5281/zenodo.12345679",
                    },
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
            index=2,
            bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
        ),
        PersistentIdentifier(  # recid
            id="10126",  # this called is mocked and will not increment the counter
            pid_type="recid",
            pid_value="12345679",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823387",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # doi
            id="10126",
            pid_type="doi",
            pid_value="10.5281/zenodo.12345679",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823387",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # oai
            id="10127",
            pid_type="oai",
            pid_value="oai:zenodo.org:12345679",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823387",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
    ]

    expected_rows_d_v1 = [
        RDMDraftMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823386",
            json={
                "id": "12345678",
                "pid": {
                    "pk": "10123",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "R",
                },
                "pids": {
                    "doi": {
                        "provider": "external",
                        "identifier": "10.1234/foo",
                    },
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
            index=1,
            bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=1,
        ),
    ]

    assert len(rows) == 12
    # v1 rows not asserted since they are checked at test_single_record_generate_rows
    assert rows[7:11] == expected_rows_v2
    assert rows[11:12] == expected_rows_d_v1

    assert len(cache["parents"].all()) == 2  # pre-existing and new
    assert len(cache["records"].all()) == 2  # two added records


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.pid_pk", mock_pid_pk
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_record_and_new_version_draft_generate_rows(
    cache, restart_pid_pk, transformed_record_entry_pks, transformed_draft_entry_pks
):
    """A published record (v1) with a new version draft (v2)."""
    tgs = [
        RDMRecordTableGenerator(
            parents_cache=cache["parents"],
            records_cache=cache["records"],
            communities_cache=cache["communities"],
        ),
        RDMDraftTableGenerator(
            parents_cache=cache["parents"],
            records_cache=cache["records"],
            communities_cache=cache["communities"],
        ),
    ]

    v1 = transformed_record_entry_pks
    v2 = deepcopy(transformed_record_entry_pks)
    v2["record"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823387"
    v2["record"]["index"] = 2
    v2["record"]["json"]["id"] = "12345679"
    v2["record"]["json"]["pid"]["pk"] = "10126"  # pk, not pid value
    v2["record"]["json"]["pids"]["oai"]["identifier"] = "oai:zenodo.org:12345679"
    v2["record"]["json"]["pids"]["doi"]["identifier"] = "10.5281/zenodo.12345679"
    d_v3 = transformed_draft_entry_pks
    d_v3["draft"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823389"
    d_v3["draft"]["json"]["id"] = "12345680"
    d_v3["draft"]["json"]["pid"]["pk"] = "10128"  # pk, not pid value, same as v1
    d_v3["draft"]["json"]["pids"]["doi"]["identifier"] = "10.1234/bar"

    rows = []
    for entry in [v1, v2, d_v3]:
        for tg in tgs:
            rows.extend(list(tg._generate_rows(entry)))

    expected_rows_d_v3 = [
        RDMDraftMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823389",
            json={
                "id": "12345680",
                "pid": {
                    "pk": "10128",
                    "obj_type": "rec",
                    "pid_type": "recid",
                    "status": "N",
                },
                "pids": {
                    "doi": {
                        "provider": "external",
                        "identifier": "10.1234/bar",
                    },
                },
            },
            created="2023-01-01 12:00:00.00000",
            updated="2023-01-31 12:00:00.00000",
            version_id=1,
            index=1,
            bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=None,
        ),
        PersistentIdentifier(  # recid
            id="10128",  # this called is mocked and will not increment the counter
            pid_type="recid",
            pid_value="12345680",
            status="N",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823389",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
    ]

    assert len(rows) == 13

    # v1 rows not asserted since they are checked at test_single_record_generate_rows
    # v2 rows not asserted since they are checked at test_record_versions_and_old_draft_generate_rows
    assert rows[11:13] == expected_rows_d_v3

    assert len(cache["parents"].all()) == 2  # pre-existing and new
    assert len(cache["records"].all()) == 2  # two added records
