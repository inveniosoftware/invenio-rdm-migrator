# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IDs generation tests."""

from uuid import UUID

from invenio_rdm_migrator.load.ids import (
    generate_pk,
    generate_recid,
    generate_uuid,
    pid_pk,
)


def test_valid_input():
    uuid = generate_uuid(None)
    assert isinstance(uuid, str)
    UUID(uuid)  # will raise ValueError if its not a UUID


def test_max_pid_pk(state):
    """Test max pid pk value changes."""
    # check state is empty
    assert not state.VALUES.get("max_pid_pk")
    # create pid
    val = pid_pk()
    # check state has been created
    assert val == state.VALUES.get("max_pid_pk")["value"]
    # create another pid
    val_inc = pid_pk()
    # check the state has been incremented
    inc_val = val + 1
    assert inc_val == val_inc
    assert val_inc == state.VALUES.get("max_pid_pk")["value"]


def test_generate_pk_returns_integer():
    assert isinstance(generate_pk(None), int)


def test_recid_default_status():
    rec_id = generate_recid({})
    assert rec_id["status"] == "R"


def test_recid_custom_status():
    rec_id = generate_recid({}, "C")
    assert rec_id["status"] == "C"


def test_recid_return_value_types():
    rec_id = generate_recid({})
    assert isinstance(rec_id["pk"], int)
    assert rec_id["obj_type"] == "rec"
    assert rec_id["pid_type"] == "recid"
