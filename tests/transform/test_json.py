# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSON transformation tests."""

from invenio_rdm_migrator.transform import JSONTransformMixin


def test_load_json_fields():
    data = {"json_field": '{"some": "value", "another":[1,2,3]}', "not_json": "test"}

    class TestTransform(JSONTransformMixin):
        """Test JSON transform."""

        pass

    transform = TestTransform()
    transform._load_json_fields(data=data, fields=["json_field"])

    assert data == {
        "json_field": {"some": "value", "another": [1, 2, 3]},
        "not_json": "test",
    }
