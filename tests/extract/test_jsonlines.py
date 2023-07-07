# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSONLines extract tests."""

from pathlib import Path
from types import GeneratorType

import jsonlines
import pytest

from invenio_rdm_migrator.extract.jsonlines import JSONLExtract


@pytest.fixture(scope="function")
def jsonlines_file(tmp_dir):
    """Returns the file path of a jsonlines file."""
    filename = Path(tmp_dir.name) / "test.jsonl"
    with jsonlines.open(filename, mode="w") as writer:
        writer.write({"key": "1", "value": "one"})
        writer.write({"key": "2", "value": "two"})

    # note there is no need for cleanup since tmp will do so and it's function scoped
    yield filename


def test_constructor_sets_filepath_attribute(jsonlines_file):
    extract = JSONLExtract(jsonlines_file)
    assert extract.filepath == jsonlines_file


def test_run_returns_iterator(jsonlines_file):
    extract = JSONLExtract(filepath=jsonlines_file)
    assert isinstance(extract.run(), GeneratorType)


def test_constructor_raises_FileNotFoundError():
    with pytest.raises(FileNotFoundError):
        JSONLExtract("invalid_filepath.jsonl")


def test_reads_jsonlines_file(jsonlines_file):
    extract = JSONLExtract(filepath=jsonlines_file)
    assert len(list(extract.run())) == 2
