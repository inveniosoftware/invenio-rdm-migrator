# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Logging module."""

import logging
import sys


class Logger:
    """Migrator logger."""

    @classmethod
    def initialize(cls, log_dir):
        """Constructor."""
        logger = logging.getLogger("migrator")
        logger.setLevel(logging.ERROR)
        # errors to file
        fh = logging.FileHandler(log_dir / "error.log")
        fh.setLevel(logging.ERROR)
        logger.addHandler(fh)
        # info to stream/stdout
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)

    @classmethod
    def get_logger(cls):
        """Get migration logger."""
        return logging.getLogger("migrator")
