# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Records/Drafts table generator tests."""

from copy import deepcopy
from unittest.mock import patch

from invenio_rdm_migrator.load.ids import pid_pk
from invenio_rdm_migrator.streams.models.pids import PersistentIdentifier
from invenio_rdm_migrator.streams.models.records import (
    RDMDraftMetadata,
    RDMParentMetadata,
    RDMRecordMetadata,
)
from invenio_rdm_migrator.streams.records.load import (
    RDMDraftTableGenerator,
    RDMRecordTableGenerator,
)

# IMPORTANT NOTE: since the resolve references method would be called externally
# (i.e. not by generate_rows) not all pid pk have consistent values coming from
# pid_pk(). Therefore, some calls are made at the beginning of the tests.


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


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.records.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_single_record_generate_rows(
    state, communities_state, parents_state, transformed_record_entry_pks
):
    """A published record with a non state parent.

    It does not make sense to also test with a state parent since that would mean
    there was a previous version of the record, which is tested separately in this module.
    """
    pid_1 = pid_pk()
    pid_2 = pid_pk()
    tg = RDMRecordTableGenerator()
    rows = list(tg._generate_rows(transformed_record_entry_pks))
    expected_rows = [
        PersistentIdentifier(  # parent recid
            id=pid_1,
            pid_type="recid",
            pid_value="12345677",
            status="R",
            object_type="rec",
            object_uuid="12345678-abcd-1a2b-3c4d-123abc456def",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        RDMParentMetadata(  # parent record
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            json={
                "id": "12345677",
                "pid": {
                    "pk": pid_1,
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
        RDMRecordMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823386",
            json={
                "id": "12345678",
                "pid": {
                    "pk": pid_2,
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
            bucket_id="bur3c0rd-1234-abcd-1ab2-1234abcd56ef",
            media_bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            deletion_status="P",
        ),
        PersistentIdentifier(  # recid
            id=pid_2,
            pid_type="recid",
            pid_value="12345678",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # doi
            id=1_000_002,
            pid_type="doi",
            pid_value="10.5281/zenodo.12345678",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823386",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # oai
            id=1_000_003,
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

    assert len(list(state.PARENTS.all())) == 2  # pre-existing and new
    assert len(list(state.RECORDS.all())) == 1


@patch(
    "invenio_rdm_migrator.streams.records.table_generators.drafts.datetime",
    MockDateTime(),
)
@patch(
    "invenio_rdm_migrator.streams.records.table_generators.parents.datetime",
    MockDateTime(),
)
def test_single_draft_generate_rows(
    state, communities_state, parents_state, transformed_draft_entry_pks
):
    """A new draft, not published."""
    pid_1 = pid_pk()
    pid_2 = pid_pk()
    tg = RDMDraftTableGenerator()
    rows = list(tg._generate_rows(transformed_draft_entry_pks))
    expected_rows = [
        PersistentIdentifier(  # parent recid
            id=pid_1,
            pid_type="recid",
            pid_value="12345677",
            status="N",
            object_type="rec",
            object_uuid="12345678-abcd-1a2b-3c4d-123abc456def",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        RDMParentMetadata(  # parent record
            id="12345678-abcd-1a2b-3c4d-123abc456def",
            json={
                "id": "12345677",
                "pid": {
                    "pk": pid_1,
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
        RDMDraftMetadata(  # record
            id="2d6970ea-602d-4e8b-a918-063a59823386",
            json={
                "id": "12345678",
                "pid": {
                    "pk": pid_2,
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
            bucket_id="b0c73700-1234-abcd-1ab2-1234abcd56ef",
            media_bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=None,
        ),
        PersistentIdentifier(  # recid
            id=pid_2,
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

    assert len(list(state.PARENTS.all())) == 2  # pre-existing and new
    assert len(list(state.RECORDS.all())) == 0


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
    state,
    communities_state,
    parents_state,
    transformed_record_entry_pks,
    transformed_draft_entry_pks,
):
    """A record with two versions (v1, v2) and a draft of the first version (v1)."""
    tgs = [
        RDMRecordTableGenerator(),
        RDMDraftTableGenerator(),
    ]

    v1 = transformed_record_entry_pks
    v2 = deepcopy(transformed_record_entry_pks)
    v2["record"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823387"
    v2["record"]["index"] = 2
    v2["record"]["json"]["id"] = "12345679"
    v2["record"]["json"]["pid"]["pk"] = 1_000_002  # pk, not pid value
    v2["record"]["json"]["pids"]["oai"]["identifier"] = "oai:zenodo.org:12345679"
    v2["record"]["json"]["pids"]["doi"]["identifier"] = "10.5281/zenodo.12345679"
    d_v1 = transformed_draft_entry_pks
    d_v1["draft"]["json"]["pid"]["pk"] = 1_000_002  # pk, not pid value, same as v1
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
                    "pk": 1_000_002,
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
            bucket_id="bur3c0rd-1234-abcd-1ab2-1234abcd56ef",
            media_bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            deletion_status="P",
        ),
        PersistentIdentifier(  # recid
            id=1_000_002,  # this called is mocked and will not increment the counter
            pid_type="recid",
            pid_value="12345679",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823387",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # doi
            id=1_000_002,
            pid_type="doi",
            pid_value="10.5281/zenodo.12345679",
            status="R",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823387",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
        PersistentIdentifier(  # oai
            id=1_000_003,
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
                    "pk": 1_000_002,
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
            bucket_id="b0c73700-1234-abcd-1ab2-1234abcd56ef",
            media_bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=1,
        ),
    ]

    assert len(rows) == 11
    # v1 rows not asserted since they are checked at test_single_record_generate_rows
    assert rows[6:10] == expected_rows_v2
    assert rows[10:11] == expected_rows_d_v1

    assert len(list(state.PARENTS.all())) == 2  # pre-existing and new
    assert len(list(state.RECORDS.all())) == 2  # two added records


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
    state,
    communities_state,
    parents_state,
    transformed_record_entry_pks,
    transformed_draft_entry_pks,
):
    """A published record (v1) with a new version draft (v2)."""
    tgs = [
        RDMRecordTableGenerator(),
        RDMDraftTableGenerator(),
    ]

    pid_1 = pid_pk()
    pid_2 = pid_pk()
    v1 = transformed_record_entry_pks
    v2 = deepcopy(transformed_record_entry_pks)
    v2["record"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823387"
    v2["record"]["index"] = 2
    v2["record"]["json"]["id"] = "12345679"
    v2["record"]["json"]["pid"]["pk"] = pid_1  # pk, not pid value
    v2["record"]["json"]["pids"]["oai"]["identifier"] = "oai:zenodo.org:12345679"
    v2["record"]["json"]["pids"]["doi"]["identifier"] = "10.5281/zenodo.12345679"
    d_v3 = transformed_draft_entry_pks
    d_v3["draft"]["id"] = "2d6970ea-602d-4e8b-a918-063a59823389"
    d_v3["draft"]["json"]["id"] = "12345680"
    d_v3["draft"]["json"]["pid"]["pk"] = pid_2  # pk, not pid value, same as v1
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
                    "pk": pid_2,
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
            bucket_id="b0c73700-1234-abcd-1ab2-1234abcd56ef",
            media_bucket_id=None,
            parent_id="12345678-abcd-1a2b-3c4d-123abc456def",
            expires_at="2024-01-01 12:00:00.00000",
            fork_version_id=None,
        ),
        PersistentIdentifier(  # recid
            id=pid_2,  # this called is mocked and will not increment the counter
            pid_type="recid",
            pid_value="12345680",
            status="N",
            object_type="rec",
            object_uuid="2d6970ea-602d-4e8b-a918-063a59823389",
            created="2023-04-01 12:00:00.00000",
            updated="2023-04-01 12:00:00.00000",
        ),
    ]

    assert len(rows) == 12

    # v1 rows not asserted since they are checked at test_single_record_generate_rows
    # v2 rows not asserted since they are checked at test_record_versions_and_old_draft_generate_rows
    assert rows[10:12] == expected_rows_d_v3

    assert len(list(state.PARENTS.all())) == 2  # pre-existing and new
    assert len(list(state.RECORDS.all())) == 2  # two added records
