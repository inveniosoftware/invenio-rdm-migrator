# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration streams."""

from datetime import datetime

from ..extract import NullExtract
from ..logging import Logger
from ..transform import IdentityTransform


class StreamDefinition:
    """ETL stream definition.

    It defines the classes that will form the ETL stream.
    """

    def __init__(self, name, extract_cls, transform_cls, load_cls):
        """Constructor."""
        self.name = name
        self.extract_cls = extract_cls
        self.transform_cls = transform_cls
        self.load_cls = load_cls


class Stream:
    """ETL stream."""

    def __init__(self, name, extract, transform, load):
        """Constructor."""
        self.name = name
        self.extract = extract or NullExtract()
        self.transform = transform or IdentityTransform()
        self.load = load

    def run(self, cleanup=False):
        """Run ETL stream."""
        logger = Logger.get_logger()

        start_time = datetime.now()
        logger.info(f"Stream {self.name} started {start_time.isoformat()}")

        extract_gen = self.extract.run()
        transform_gen = self.transform.run(extract_gen)
        self.load.run(transform_gen, cleanup=cleanup)

        end_time = datetime.now()
        logger.info(f"Stream ended {end_time.isoformat()}")

        logger.info(f"Execution time: {end_time - start_time}")
