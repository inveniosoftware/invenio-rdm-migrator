# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Requests transform tests."""

import dictdiffer

from invenio_rdm_migrator.streams.communities import CommunityEntry, CommunityTransform


class MockCommunityTransform(CommunityTransform):
    """Mock class for community data transformation."""

    def _community(self, entry):
        """Transform the community."""
        return {"key": "value"}

    def _oai_set(self, entry):
        """Transform the featured community."""
        return {"key": "value"}

    def _community_members(self, entry):
        """Tramsform the community members."""
        return {"key": "value"}

    def _featured_community(self, entry):
        """Transform the featured community."""
        return {"key": "value"}

    def _community_files(self, entry):
        return {
            "file": {"key": "value"},
            "bucket": {"key": "value"},
            "file_object": {"key": "value"},
        }


def test_community_transform():
    """Test the full community transformation."""
    result = MockCommunityTransform()._transform({})
    expected = {
        "community": {"key": "value"},
        "oai_set": {"key": "value"},
        "community_members": {"key": "value"},
        "featured_community": {"key": "value"},
        "community_files": {
            "file": {"key": "value"},
            "bucket": {"key": "value"},
            "file_object": {"key": "value"},
        },
    }
    assert not list(dictdiffer.diff(result, expected))


class MockCommunityEntry(CommunityEntry):
    """Transform a single mock community entry."""

    def _created(self, entry):
        """Transform community 'created' field."""
        return "2023-01-01 12:00:00.00000"

    def _updated(self, entry):
        """Transform community 'updated' field."""
        return "2023-01-31 12:00:00.00000"

    def _version_id(self, entry):
        """Transform community 'version_id' field."""
        return 1

    def _slug(self, entry):
        """Transform community 'slug' field."""
        return "migrator"

    def _files(self, entry):
        """Transform community 'files' field."""
        return None

    def _access(self, entry):
        """Transform community 'access' field."""
        return None

    def _bucket_id(self, entry):
        """Transform community 'bucket_id' field."""
        return 1

    def _metadata(self, entry):
        """Transform community 'metadata' field."""
        return {
            "title": "Migrator community",
            "description": "Migrator testing community",
            "page": "",
            "curation_policy": "",
        }


def test_community_entry():
    """Test the community entry transformation."""
    result = MockCommunityEntry().transform({})
    expected = {
        "created": "2023-01-01 12:00:00.00000",
        "updated": "2023-01-31 12:00:00.00000",
        "version_id": 1,
        "slug": "migrator",
        "json": {
            "files": None,
            "access": None,
            "metadata": {
                "title": "Migrator community",
                "description": "Migrator testing community",
                "page": "",
                "curation_policy": "",
            },
        },
        "bucket_id": 1,
    }

    assert not list(dictdiffer.diff(result, expected))
