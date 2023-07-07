# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Streams tests."""


from invenio_rdm_migrator.streams.streams import StreamDefinition


def test_stream_definition_attributes():
    # this tests is not super useful, just checks the attributes
    # imo, if it wasn't because it holds classes it could be a dataclass
    stream_def = StreamDefinition("test_stream", "extract", "transform", "load")
    assert stream_def.name == "test_stream"
    assert stream_def.extract_cls == "extract"
    assert stream_def.transform_cls == "transform"
    assert stream_def.load_cls == "load"
