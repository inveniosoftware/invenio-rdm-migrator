# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""State tests."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import MetaData, create_engine, insert, select
from sqlalchemy.exc import IntegrityError

from invenio_rdm_migrator.state import StateDB, StateValidator

###
# Global
###


@pytest.fixture(scope="function")
def disk_db(tmp_dir):
    """Creates a DB on disk and initializes all the migrator related tables on it."""
    db_dir = Path(tmp_dir.name) / "state.db"
    disk_eng = create_engine(f"sqlite:///{db_dir}")
    disk_meta = MetaData()
    StateDB._initialize_db(disk_meta)
    disk_meta.create_all(disk_eng)
    with disk_eng.connect() as conn:
        conn.execute(
            insert(disk_meta.tables["parents"]).values(
                {
                    "recid": "123456",
                    "id": "1234abcd-1234-5678-abcd-123abc456def",
                    "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
                    "latest_index": 1,
                },
            )
        )
        conn.execute(
            insert(disk_meta.tables["records"]).values(
                {
                    "recid": "123456",
                    "index": 1,
                    "id": "1234abcd-1234-5678-abcd-123abc456def",  # uuid
                    "parent_id": "1234abcd-1234-5678-abcd-123abc456def",  # parent uuid
                    "fork_version_id": 3,
                    "pids": {"doi": "10.1234/123456"},
                },
            )
        )
        conn.execute(
            insert(disk_meta.tables["communities"]).values(
                {
                    "slug": "test-comm",
                    "id": "1234abcd-1234-5678-abcd-123abc456def",
                    "bucket_id": "1234abcd-1234-5678-abcd-123abc456def",
                    "oai_set_id": 1,
                }
            )
        )
        conn.execute(
            insert(disk_meta.tables["global"]).values(
                {"key": "max_value_pk", "value": 1}
            )
        )

        conn.commit()

    yield disk_eng, disk_meta

    db_dir.unlink()


def test_state_with_no_initial_db(tmp_dir):
    """Test state creation without an existing db.

    Test the implicit creation of tables.
    """
    state = StateDB(db_dir=tmp_dir.name)
    # tables exist and are empty
    assert len(list(state.all("parents"))) == 0
    assert len(list(state.all("records"))) == 0
    assert len(list(state.all("communities"))) == 0
    assert len(list(state.all("pids"))) == 0
    assert len(list(state.all("global"))) == 0

    # check that no extra tables were created
    assert set(state.tables) == set(
        {
            "parents",
            "records",
            "communities",
            "global",
            "pids",
            "buckets",
            "file_records",
        }
    )


def test_state_load_from_disk(tmp_dir, disk_db):
    """Test db loading from disk into memory."""
    state = StateDB(db_dir=tmp_dir.name)

    # check the memory db status
    assert len(list(state.all("parents"))) == 1
    assert len(list(state.all("records"))) == 1
    assert len(list(state.all("communities"))) == 1
    assert len(list(state.all("global"))) == 1

    # add data to disk db and check they are not present in memory
    state.add(
        "parents",
        {
            "recid": "123455",
            "id": "1234abbb-1234-5678-abcd-123abc456def",
            "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "latest_index": 1,
        },
    )
    assert len(list(state.all("parents"))) == 2

    # check the db on disk has not been updated (prevent pollution)
    disk_eng, disk_meta = disk_db
    parents_table = disk_meta.tables["parents"]
    with disk_eng.connect() as conn:
        assert (
            len(
                list(
                    conn.execute(
                        select(parents_table).where(
                            parents_table.columns.recid == "123455"
                        )
                    ).all()
                )
            )
            == 0
        )


def test_state_save_to_disk(tmp_dir):
    """Test db persistence to disk."""
    state = StateDB(db_dir=tmp_dir.name)
    # check the memory db status
    assert len(list(state.all("parents"))) == 0
    assert len(list(state.all("records"))) == 0
    assert len(list(state.all("communities"))) == 0
    assert len(list(state.all("global"))) == 0

    # add data to disk db and check they are not present in memory
    state.add(
        "parents",
        {
            "recid": "123455",
            "id": "1234abbb-1234-5678-abcd-123abc456def",
            "latest_id": "12345678-abcd-1a2b-3c4d-123abc456def",
            "latest_index": 1,
        },
    )
    assert len(list(state.all("parents"))) == 1
    state.save()

    # check if data is saved to disk
    db_dir = Path(tmp_dir.name) / "state.db"
    disk_eng = create_engine(f"sqlite:///{db_dir}")
    disk_meta = MetaData()
    _ = StateDB._initialize_db(disk_meta)
    disk_meta.create_all(disk_eng)

    parents_table = disk_meta.tables["parents"]
    with disk_eng.connect() as conn:
        assert (
            len(
                list(
                    conn.execute(
                        select(parents_table).where(
                            parents_table.columns.recid == "123455"
                        )
                    ).all()
                )
            )
            == 1
        )


def test_state_save_to_disk_alt_filename(tmp_dir):
    """Test db persistence to disk with a different filename."""
    state = StateDB(db_dir=tmp_dir.name)
    state.save(filename="altname.db")
    assert (Path(tmp_dir.name) / "altname.db").exists()


def test_state_save_to_disk_alt_filepath(tmp_dir):
    """Test db persistence to disk on a different path."""
    state = StateDB(db_dir=tmp_dir.name)

    alt_dir = tempfile.TemporaryDirectory()
    alt_path = Path(alt_dir.name) / "altpath.db"

    state.save(filepath=alt_path)
    assert alt_path.exists()

    alt_dir.cleanup()


###
# Parent State
# record uuid = d3c0dd1d...
# parent uuid = f4d3071d...
###


def test_parent_state_record_entry(parents_state):
    parents_state.PARENTS.add(
        "123",
        {
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "latest_index": 1,
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert parents_state.PARENTS.get("123")


def test_parent_state_draft_entry(parents_state):
    parents_state.PARENTS.add(
        "123",
        {
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "next_draft_id": "dd4f71d0-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert parents_state.PARENTS.get("123")


def test_parent_state_update_record(parents_state):
    parents_state.PARENTS.add(
        "123",
        {
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "latest_index": 1,
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert not parents_state.PARENTS.get("123").get("next_draft_id")

    parents_state.PARENTS.update(
        "123",
        {
            "latest_index": 100,
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert parents_state.PARENTS.get("123").get("latest_index") == 100
    assert (
        parents_state.PARENTS.get("123").get("latest_id")
        == "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef"
    )


def test_parent_state_update_draft(parents_state):
    parents_state.PARENTS.add(
        "123",
        {
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "latest_index": 1,
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert not parents_state.PARENTS.get("123").get("next_draft_id")

    parents_state.PARENTS.update(
        "123",
        {
            "next_draft_id": "dd4f71d0-1234-abcd-1ab2-1234abcd56ef",
        },
    )
    assert (
        parents_state.PARENTS.get("123").get("next_draft_id")
        == "dd4f71d0-1234-abcd-1ab2-1234abcd56ef"
    )


def test_parent_state_invalid_entries(parents_state):
    invalid_by_db_constraints = [
        {  # no id
            "latest_index": 1,
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
    ]

    for entry in invalid_by_db_constraints:
        pytest.raises(IntegrityError, parents_state.PARENTS.add, "123", entry)

    invalid_by_validator = [
        {  # missing lastest index
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "latest_id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
        },
        {  # no latest id nor next draft id
            "id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "latest_index": 1,
        },
    ]

    for entry in invalid_by_validator:
        pytest.raises(AssertionError, parents_state.PARENTS.add, "123", entry)


###
# Record State
###


def test_record_state_record_entry(state):
    state.RECORDS.add(
        "123",
        {
            "index": 1,
            "id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
            "parent_id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "fork_version_id": 1,
        },
    )
    assert state.RECORDS.get("123")


def test_record_state_invalid_entries(state):
    invalid = [
        {  # missing index
            "id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
            "parent_id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "fork_version_id": 1,
        },
        {  # missing id
            "index": 1,
            "parent_id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
            "fork_version_id": 1,
        },
        {  # missing parent_id
            "index": 1,
            "id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
            "fork_version_id": 1,
        },
        {  # missing fork_version_id
            "index": 1,
            "id": "d3c0dd1d-1234-abcd-1ab2-1234abcd56ef",
            "parent_id": "f4d3071d-1234-abcd-1ab2-1234abcd56ef",
        },
    ]

    for entry in invalid:
        pytest.raises(IntegrityError, state.RECORDS.add, "123", entry)


###
# PIDs State
###


def test_pids_state_valid(state):
    created = datetime.fromtimestamp(1688045928)
    state.PIDS.add(
        "123",
        {
            "id": 1_000_000,
            "pid_type": "recid",
            "status": "K",
            "created": created,
        },
    )
    state.PIDS.add(
        "124",
        {
            "id": 1000001,
            "pid_type": "recid",
            "status": "K",
            "obj_type": "rec",
            "created": created,
        },
    )

    assert state.PIDS.get("123")
    assert state.PIDS.get("124")


def test_pids_state_duplicated_id(state):
    created = datetime.fromtimestamp(1688045928)
    state.PIDS.add(
        "123",
        {
            "id": 1_000_000,  # has a unique constraint
            "pid_type": "recid",
            "status": "K",
            "created": created,
        },
    )

    pytest.raises(
        IntegrityError,
        state.PIDS.add,
        "124",  # diff pk to make sure it fails on id
        {
            "id": 1_000_000,  # has a unique constraint
            "pid_type": "recid",
            "status": "K",
            "created": created,
        },
    )


def test_pids_state_invalid_entries(state):
    created = datetime.fromtimestamp(1688045928)
    invalid = [
        {  # missing id
            "pid_type": "recid",
            "status": "K",
            "obj_type": "rec",
            "created": created,
        },
        {  # missing pid_type
            "id": 1_000_000,
            "status": "K",
            "obj_type": "rec",
            "created": created,
        },
        {  # missing status
            "id": 1_000_000,
            "pid_type": "recid",
            "obj_type": "rec",
            "created": created,
        },
        {  # missing created
            "id": 1_000_000,
            "status": "K",
            "pid_type": "recid",
            "obj_type": "rec",
        },
    ]

    for idx, entry in enumerate(invalid):
        pytest.raises(IntegrityError, state.PIDS.add, idx, entry)


###
# StateValidator
###


def test_default_validator():
    # test that the interface holds
    assert StateValidator.validate({}) == False


###
# Bucket State
###


def test_bucket_state_valid(state):
    state.BUCKETS.add(
        "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        {"draft_id": "d94f793c-47d2-48e2-9867-ca597b4ebb41"},
    )

    assert state.BUCKETS.get("0e12b4b6-9cc7-46df-9a04-c11c478de211")


def test_buckets_state_invalid_entries(state):
    pytest.raises(
        IntegrityError,
        state.BUCKETS.add,
        "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        {},  # empty
    )


def test_delete_bucket_state(state):
    state.BUCKETS.add(
        "0e12b4b6-9cc7-46df-9a04-c11c478de211",
        {"draft_id": "d94f793c-47d2-48e2-9867-ca597b4ebb41"},
    )

    state.BUCKETS.delete("0e12b4b6-9cc7-46df-9a04-c11c478de211")
    assert not state.BUCKETS.get("0e12b4b6-9cc7-46df-9a04-c11c478de211")


###
# File Records
###


def test_file_record_state(state):
    state.FILE_RECORDS.add(
        "e94b243e-9c0c-44df-bd1f-6decc374cf78",
        {
            "json": {},
            "created": "2023-06-29T13:00:00",
            "updated": "2023-06-29T14:00:00",
            "version_id": 1,
            "key": "IMG_3535.jpg",
            "record_id": "93c09d1d-47d2-48e2-9867-ca597b4ebb41",
            "object_version_id": "f8200dc7-55b6-4785-abd0-f3d13b143c98",
        },
    )

    assert state.FILE_RECORDS.get("e94b243e-9c0c-44df-bd1f-6decc374cf78")


def test_file_record_state_search(state):
    state.FILE_RECORDS.add(
        "e94b243e-9c0c-44df-bd1f-6decc374cf78",
        {
            "json": {},
            "created": "2023-06-29T13:00:00",
            "updated": "2023-06-29T14:00:00",
            "version_id": 1,
            "key": "IMG_3535.jpg",
            "record_id": "93c09d1d-47d2-48e2-9867-ca597b4ebb41",
            "object_version_id": "f8200dc7-55b6-4785-abd0-f3d13b143c98",
        },
    )
    state.FILE_RECORDS.add(
        "e94b243e-9c0c-44df-bd1f-6decc374cf79",
        {
            "json": {},
            "created": "2023-06-29T13:00:00",
            "updated": "2023-06-29T14:00:00",
            "version_id": 1,
            "key": "IMG_3535.jpg",
            "record_id": "93c09d1d-47d2-48e2-9867-ca597b4ebb41",
            "object_version_id": "f8200dc7-55b6-4785-abd0-f3d13b143c98",
        },
    )

    files = state.FILE_RECORDS.search(
        "record_id", "93c09d1d-47d2-48e2-9867-ca597b4ebb41"
    )
    assert len(list(files)) == 2
