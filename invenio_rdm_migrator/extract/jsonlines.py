# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
