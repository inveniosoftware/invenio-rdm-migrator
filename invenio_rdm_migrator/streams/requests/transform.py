# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration requests transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class RequestTransform(Transform):
    """Base class for request data transformation."""

    @abstractmethod
    def _request(self, entry):
        """Transform the request."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        return self._request(entry)


class RequestEntry(Entry):
    """Transform a single request entry."""

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date of the request."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date of the request."""
        pass

    @abstractmethod
    def _version_id(self, entry):
        """Returns the version id of the request.

        {Elastic,Open}search will fail with values lower than 1.
        """
        pass

    @abstractmethod
    def _json(self, entry):
        """Returns the request json body."""
        pass

    @abstractmethod
    def _number(self, entry):
        """Returns the request number."""
        pass

    @abstractmethod
    def _expires_at(self, entry):
        """Returns the request expiration date."""
        pass

    def transform(self, entry):
        """Transform a request single entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "version_id": self._version_id(entry),
            "json": self._json(entry),
            "number": self._number(entry),
            "expires_at": self._expires_at(entry),
        }


class InclusionRequestEntry(RequestEntry):
    """Inclusion request entry."""

    @abstractmethod
    def _title(self, entry):
        """Returns the request title."""
        pass

    @abstractmethod
    def _topic(self, entry):
        """Returns the request topic."""
        pass

    @abstractmethod
    def _receiver(self, entry):
        """Returns the request receiver."""
        pass

    @abstractmethod
    def _created_by(self, entry):
        """Returns the request creation reference."""
        pass

    def _json(self, entry):
        """Returns the request json body."""
        return {
            "type": "community-inclusion",
            "title": self._title(entry),
            "topic": self._topic(entry),
            "status": "submitted",
            "receiver": self._receiver(entry),
            "created_by": self._created_by(entry),
            "$schema": "local://requests/request-v1.0.0.json",
        }
