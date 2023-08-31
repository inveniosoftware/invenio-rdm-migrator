# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSONLines extract."""

from pathlib import Path

import orjson

from invenio_rdm_migrator.extract import Extract


class JSONLExtract(Extract):
    """Data extraction from JSONL files."""

    def __init__(self, filepath):
        """Constructor."""
        if not Path(filepath).exists():
            raise FileNotFoundError(filepath)

        self.filepath = filepath

    def run(self):
        """Yield one element at a time."""
        with open(self.filepath, "rb") as reader:
            for line in reader:
                yield orjson.loads(line)
