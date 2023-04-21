# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class FilesTransform(Transform):
    """Base class for user data transformation."""

    @abstractmethod
    def _bucket(self, entry):
        """Transform the bucket."""
        pass

    @abstractmethod
    def _object_version(self, entry):
        """Transform the object_version."""
        pass

    @abstractmethod
    def _file(self, entry):
        """Transform the file."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "bucket": self._bucket(entry),
            "object_version": self._object_version(entry),
            "file": self._file(entry),
        }


class FilesBucketEntry(Entry):
    """Transform a single file bucket entry."""

    @abstractmethod
    def _id(self, entry):
        """Returns the file bucket ID."""
        pass

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _default_location(self, entry):
        """Returns the file bucket default location."""
        pass

    @abstractmethod
    def _default_storage_class(self, entry):
        """Returns the file bucket default storage class."""
        pass

    @abstractmethod
    def _size(self, entry):
        """Returns the file bucket size."""
        pass

    @abstractmethod
    def _quota_size(self, entry):
        """Returns the file bucket quota size."""
        pass

    @abstractmethod
    def _max_file_size(self, entry):
        """Returns the file bucket max file size."""
        pass

    @abstractmethod
    def _locked(self, entry):
        """Returns if the file bucket is locked."""
        pass

    @abstractmethod
    def _deleted(self, entry):
        """Returns if the file bucket is deleted."""
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "id": self._id(entry),
            "created": self._created(entry),
            "updated": self._updated(entry),
            "default_location": self._default_location(entry),
            "default_storage_class": self._default_storage_class(entry),
            "size": self._size(entry),
            "quota_size": self._quota_size(entry),
            "max_file_size": self._max_file_size(entry),
            "locked": self._locked(entry),
            "deleted": self._deleted(entry),
        }


class FilesObjectVersionEntry(Entry):
    """Transform a single file object version entry."""

    @abstractmethod
    def _version_id(self, entry):
        """Returns the file object version ID."""
        pass

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _key(self, entry):
        """Returns the file key name."""
        pass

    @abstractmethod
    def _bucket_id(self, entry):
        """Returns the file object version bucket ID i.e associated bucket."""
        pass

    @abstractmethod
    def _file_id(self, entry):
        """Returns the file object version file ID i.e associated file."""
        pass

    @abstractmethod
    def _mimetype(self, entry):
        """Returns the file object version mimetype."""
        pass

    @abstractmethod
    def _is_head(self, entry):
        """Returns if the file object version is head i.e the latest."""
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "version_id": self._version_id(entry),
            "created": self._created(entry),
            "updated": self._updated(entry),
            "key": self._key(entry),
            "bucket_id": self._bucket_id(entry),
            "file_id": self._file_id(entry),
            "_mimetype": self._mimetype(entry),
            "is_head": self._is_head(entry),
        }


class FilesInstanceEntry(Entry):
    """Transform a single file instance entry."""

    @abstractmethod
    def _id(self, entry):
        """Returns the file instance ID."""
        pass

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _uri(self, entry):
        """Returns the file uri."""
        pass

    @abstractmethod
    def _storage_class(self, entry):
        """Returns the file instance storage class."""
        pass

    @abstractmethod
    def _size(self, entry):
        """Returns the file instance size."""
        pass

    @abstractmethod
    def _checksum(self, entry):
        """Returns the file instance checksum."""
        pass

    @abstractmethod
    def _readable(self, entry):
        """Returns if the file instance can be read."""
        pass

    @abstractmethod
    def _writable(self, entry):
        """Returns if the file instance can be written."""
        pass

    @abstractmethod
    def _last_check_at(self, entry):
        """Returns the last date the file was checked."""
        pass

    @abstractmethod
    def _last_check(self, entry):
        """Returns if the file instance was last checked."""
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "id": self._id(entry),
            "created": self._created(entry),
            "updated": self._updated(entry),
            "uri": self._uri(entry),
            "storage_class": self._storage_class(entry),
            "size": self._size(entry),
            "checksum": self._checksum(entry),
            "readable": self._readable(entry),
            "writable": self._writable(entry),
            "last_check_at": self._last_check_at(entry),
            "last_check": self._last_check(entry),
        }
