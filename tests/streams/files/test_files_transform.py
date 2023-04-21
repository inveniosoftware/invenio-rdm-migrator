# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Requests transform tests."""

import dictdiffer

from invenio_rdm_migrator.streams.files import (
    FilesBucketEntry,
    FilesInstanceEntry,
    FilesObjectVersionEntry,
    FilesTransform,
)


class MockFilesTransform(FilesTransform):
    """Mock class for files data transformation."""

    def _bucket(self, entry):
        """Transform the bucket."""
        return {"id": "1"}

    def _object_version(self, entry):
        """Transform the object_version."""
        return {"id": "1"}

    def _file(self, entry):
        """Transform the file."""
        return {"id": "1"}


def test_files_transform():
    """Test the full files transformation."""
    result = MockFilesTransform()._transform({})
    expected = {
        "bucket": {"id": "1"},
        "object_version": {"id": "1"},
        "file": {"id": "1"},
    }
    assert not list(dictdiffer.diff(result, expected))


class MockFilesBucketEntry(FilesBucketEntry):
    """Transform a single mock files bucket entry."""

    def _id(self, entry):
        """Returns the file bucket ID."""
        return "1"

    def _created(self, entry):
        """Returns the creation date."""
        return "2023-04-19"

    def _updated(self, entry):
        """Returns the update date."""
        return "2023-04-19"

    def _default_location(self, entry):
        """Returns the file bucket default location."""
        return "1"

    def _default_storage_class(self, entry):
        """Returns the file bucket default storage class."""
        return "L"

    def _size(self, entry):
        """Returns the file bucket size."""
        return 1234

    def _quota_size(self, entry):
        """Returns the file bucket quota size."""
        return None

    def _max_file_size(self, entry):
        """Returns the file bucket max file size."""
        return None

    def _locked(self, entry):
        """Returns if the file bucket is locked."""
        return False

    def _deleted(self, entry):
        """Returns if the file bucket is deleted."""
        return False


def test_files_bucket_entry():
    """Test the files bucket entry transformation."""
    result = MockFilesBucketEntry().transform({})
    expected = {
        "id": "1",
        "created": "2023-04-19",
        "updated": "2023-04-19",
        "default_location": "1",
        "default_storage_class": "L",
        "size": 1234,
        "quota_size": None,
        "max_file_size": None,
        "locked": False,
        "deleted": False,
    }

    assert not list(dictdiffer.diff(result, expected))


class MockFilesObjectVersionEntry(FilesObjectVersionEntry):
    """Transform a single mock files bucket entry."""

    def _version_id(self, entry):
        """Returns the file object version ID."""
        return "2"

    def _created(self, entry):
        """Returns the creation date."""
        return "2023-04-19"

    def _updated(self, entry):
        """Returns the update date."""
        return "2023-04-19"

    def _key(self, entry):
        """Returns the file key name."""
        return "file.txt"

    def _bucket_id(self, entry):
        """Returns the file object version bucket ID i.e associated bucket."""
        return "1"

    def _file_id(self, entry):
        """Returns the file object version file ID i.e associated file."""
        return "3"

    def _mimetype(self, entry):
        """Returns the file object version mimetype."""
        return None

    def _is_head(self, entry):
        """Returns if the file object version is head i.e the latest."""
        return True


def test_files_object_version_entry():
    """Test the files object version entry transformation."""
    result = MockFilesObjectVersionEntry().transform({})
    expected = {
        "version_id": "2",
        "created": "2023-04-19",
        "updated": "2023-04-19",
        "key": "file.txt",
        "bucket_id": "1",
        "file_id": "3",
        "_mimetype": None,
        "is_head": True,
    }

    assert not list(dictdiffer.diff(result, expected))


class MockFilesInstanceEntry(FilesInstanceEntry):
    """Transform a single mock files bucket entry."""

    def _id(self, entry):
        """Returns the file instance ID."""
        return "3"

    def _created(self, entry):
        """Returns the creation date."""
        return "2023-04-19"

    def _updated(self, entry):
        """Returns the update date."""
        return "2023-04-19"

    def _uri(self, entry):
        """Returns the file uri."""
        return "path/to/file"

    def _storage_class(self, entry):
        """Returns the file instance storage class."""
        return "L"

    def _size(self, entry):
        """Returns the file instance size."""
        return 1234

    def _checksum(self, entry):
        """Returns the file instance checksum."""
        return "md5:abcd1234"

    def _readable(self, entry):
        """Returns if the file instance can be read."""
        return True

    def _writable(self, entry):
        """Returns if the file instance can be written."""
        return True

    def _last_check_at(self, entry):
        """Returns the last date the file was checked."""
        return None

    def _last_check(self, entry):
        """Returns if the file instance was last checked."""
        return False


def test_files_instance_entry():
    """Test the files instance entry transformation."""
    result = MockFilesInstanceEntry().transform({})
    expected = {
        "id": "3",
        "created": "2023-04-19",
        "updated": "2023-04-19",
        "uri": "path/to/file",
        "storage_class": "L",
        "size": 1234,
        "checksum": "md5:abcd1234",
        "readable": True,
        "writable": True,
        "last_check_at": None,
        "last_check": False,
    }

    assert not list(dictdiffer.diff(result, expected))
