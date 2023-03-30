# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class CommunityTransform(Transform):
    """Base class for community data transformation."""

    @abstractmethod
    def _community(self, entry):
        """Transform the community."""
        pass

    @abstractmethod
    def _community_members(self, entry):
        """Transform the community members."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "community": self._community(entry),
            "community_members": self._community_members(entry),
        }


class CommunityEntry(Entry):
    """Transform a single community entry."""

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _version_id(self, entry):
        """Returns the version id.

        {Elastic,Open}search will fail with values lower than 1.
        """
        pass

    @abstractmethod
    def _slug(self, entry):
        """Returns the community slug."""
        pass

    @abstractmethod
    def _files(self, entry):
        """Transform the files of a record."""
        pass

    @abstractmethod
    def _access(self, entry):
        """Transform the access of a record."""
        pass

    @abstractmethod
    def _bucket_id(self, entry):
        """Returns the community bucket id ."""
        pass

    @abstractmethod
    def _metadata(self, entry):
        """Transform the metadata of a community.

        No schema/dictionary is enforced as choice balanced between
        duplicating the schema with abstract methods and allowing for flexibility
        i.e. different metadata schema.
        """
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "version_id": self._version_id(entry),
            "slug": self._slug(entry),
            "json": {
                "files": self._files(entry),
                "access": self._access(entry),
                "metadata": self._metadata(entry),
            },
            "bucket_id": self._bucket_id(entry),
        }


class CommunityMemberEntry(Entry):
    """Transform a community members."""

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _version_id(self, entry):
        """Returns the version id.

        {Elastic,Open}search will fail with values lower than 1.
        """
        pass

    @abstractmethod
    def _role(self, entry):
        """Returns the community member role."""
        pass

    @abstractmethod
    def _visible(self, entry):
        """Returns if the community member is visible or not."""
        pass

    @abstractmethod
    def _active(self, entry):
        """Returns if the community member is active or not."""
        pass

    @abstractmethod
    def _user_id(self, entry):
        """Returns the community member user id, if the member is a single user."""
        pass

    @abstractmethod
    def _group_id(self, entry):
        """Returns the community member group id, if the member is a group."""
        pass

    @abstractmethod
    def _request_id(self, entry):
        """Returns the community member request id."""
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "json": {},
            "version_id": self._version_id(entry),
            "role": self._role(entry),
            "visible": self._visible(entry),
            "active": self._active(entry),
            "user_id": self._user_id(entry),
            "group_id": self._group_id(entry),
            "request_id": self._request_id(entry),
        }


class ParentCommunityEntry(Entry):
    """Transform a single parent community entry."""

    @abstractmethod
    def _community(self, entry):
        """Returns the community slug."""
        pass

    @abstractmethod
    def _record(self, entry):
        """Returns the record pid."""
        pass

    @abstractmethod
    def _request(self, entry):
        """Returns the request id."""
        pass

    def transform(self, entry):
        """Transform a record single entry."""
        return {
            "community": self._community(entry),
            "record": self._record(entry),
            "request": self._request(entry),
        }
