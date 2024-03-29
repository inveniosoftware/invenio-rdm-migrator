# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class RDMRecordTransform(Transform):
    """Base class for record data transformation."""

    @abstractmethod
    def _parent(self, entry):
        """Transform the parent record."""
        pass

    @abstractmethod
    def _record(self, entry):
        """Transform the record."""
        pass

    @abstractmethod
    def _draft(self, entry):
        """Transform the draft."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        # the functions receive the full record/data entry
        # while in most cases the full view is not needed
        # since this is a low level tool used only by users
        # with deep system knowledge providing the flexibility
        # is future proofing and simplifying the interface
        return {
            "record": self._record(entry),
            "draft": self._draft(entry),
            "parent": self._parent(entry),
        }


class RDMRecordEntry(Entry):
    """Transform a single record entry."""

    def _schema(self, entry):
        """Return JSONSchema of the record."""
        return "local://records/record-v6.0.0.json"

    @abstractmethod
    def _id(self, entry):
        """Returns the rdm record uuid."""
        pass

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date of the record."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date of the record."""
        pass

    @abstractmethod
    def _version_id(self, entry):
        """Returns the version id of the record.

        {Elastic,Open}search will fail with values lower than 1.
        """
        pass

    @abstractmethod
    def _index(self, entry):
        """Returns the index of the record."""
        pass

    @abstractmethod
    def _recid(self, entry):
        """Returns the recid of the record."""
        pass

    @abstractmethod
    def _pids(self, entry):
        """Returns the pids of the record."""
        pass

    @abstractmethod
    def _bucket_id(self, entry):
        """Returns the bucket id of the record."""
        pass

    @abstractmethod
    def _media_bucket_id(self, entry):
        """Returns the bucket id of the record."""
        pass

    @abstractmethod
    def _files(self, entry):
        """Transform the files of a record."""
        pass

    @abstractmethod
    def _media_files(self, entry):
        """Transform the media files of a record."""
        pass

    @abstractmethod
    def _access(self, entry):
        """Transform the access of a record."""
        pass

    @abstractmethod
    def _metadata(self, entry):
        """Transform the metadata of a record.

        No schema/dictionary is enforced as choice balanced between
        duplicating the schema with abstract methods and allowing for flexibility
        i.e. different metadata schema.
        """
        pass

    @abstractmethod
    def _custom_fields(self, entry):
        """Transform the custom fields of a record."""
        pass

    def transform(self, entry):
        """Transform a record single entry."""
        transformed = {}
        self._load_partial(
            entry,
            transformed,
            [
                "id",
                "created",
                "updated",
                "version_id",
                "index",
                "bucket_id",
                "media_bucket_id",
            ],
        )
        # json might give an inner KeyError that should not be masked
        self._load_partial(
            entry,
            transformed,
            [
                ("id", "recid"),
                ("$schema", "schema"),
                "pids",
                "files",
                "media_files",
                "metadata",
                "access",
                "custom_fields",
            ],
            prefix="json",
        )

        return transformed


class RDMRecordFileEntry(Entry):
    """Transform a single record file entry.

    Connects records with files.
    """

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _json(self, entry):
        """Returns the rdm record file metadata."""
        pass

    @abstractmethod
    def _version_id(self, entry):
        """Returns the rdm record file version id."""
        pass

    @abstractmethod
    def _key(self, entry):
        """Returns the rdm record file key name."""
        pass

    @abstractmethod
    def _object_version_id(self, entry):
        """Returns the associated file object version ID."""
        pass

    def transform(self, entry):
        """Transform a single record files entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "json": self._json(entry),
            "version_id": self._version_id(entry),
            "key": self._key(entry),
            "object_version_id": self._object_version_id(entry),
        }
