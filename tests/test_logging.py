# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Logging tests."""


from invenio_rdm_migrator.logging import Logger

# NOTE this tests will actually print so they will display in the console when running
# pytest. However, they will pass.


def test_log_info_to_stdout(capsys, tmp_path):
    Logger.initialize(tmp_path)
    logger = Logger.get_logger()

    logger.info("safe to ignore: Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.err


def test_log_error_to_file(tmp_path):
    Logger.initialize(tmp_path)
    logger = Logger.get_logger()

    with open(tmp_path / "error.log", "r") as f:
        logger.error("safe to ignore: Test error message")
        assert "Test error message" in f.read()

        logger.info("safe to ignore: Test info message")
        assert not "Test info message" in f.read()
