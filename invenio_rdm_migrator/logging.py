# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Logging module."""

import dataclasses
import logging

from pythonjsonlogger import jsonlogger


class DataclassJSONEncoder(jsonlogger.JsonEncoder):
    """JSON encoder for serializing dataclasses as ``dict``."""

    def default(self, o):
        """Encoder."""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class Logger:
    """Migrator logger."""

    @classmethod
    def initialize(cls, log_dir):
        """Constructor."""
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        logger = logging.getLogger("migrator")
        logger.setLevel(logging.INFO)
        # errors to file
        fh = logging.FileHandler(log_dir / "error.log")
        fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # info to stream/stdout
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)

    @classmethod
    def get_logger(cls):
        """Get migration logger."""
        return logging.getLogger("migrator")


class FailedTxLogger:
    """Failed transactions logger."""

    name = "migrator.failed_tx"

    @classmethod
    def initialize(cls, log_dir):
        """Constructor."""
        formatter = jsonlogger.JsonFormatter(json_encoder=DataclassJSONEncoder)

        logger = logging.getLogger(cls.name)
        fh = logging.FileHandler(log_dir / "failed-tx.log")
        fh.setFormatter(formatter)
        fh.setLevel(logging.ERROR)
        logger.addHandler(fh)
        # info to stream/stdout
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)

    @classmethod
    def get_logger(cls):
        """Get migration logger."""
        return logging.getLogger(cls.name)
