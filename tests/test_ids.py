# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IDs tests."""

from invenio_rdm_migrator.load.ids import pid_pk


def test_max_pid_pk(global_state):
    """Test max pid pk value changes."""
    # check state is empty
    assert not global_state.get("max_pid_pk")
    # create pid
    val = pid_pk()
    # check state has been created
    assert val == str(global_state.get("max_pid_pk")["value"])
    # create another pid
    val_inc = pid_pk()
    # check the state has been incremented
    inc_val = str(int(val) + 1)
    assert inc_val == val_inc
    assert val_inc == str(global_state.get("max_pid_pk")["value"])
