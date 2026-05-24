# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
