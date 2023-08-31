# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration GtiHub transform interfaces."""

from ...transform import Transform


class GitHubReleaseTransform(Transform):
    """GitHub release transformation."""

    def _created(self, entry):
        """Return created."""
        return entry["created"]

    def _updated(self, entry):
        """Return updated."""
        return entry["updated"]

    def _id(self, entry):
        """Return id."""
        return entry["id"]

    def _release_id(self, entry):
        """Return release_id."""
        return entry["release_id"]

    def _tag(self, entry):
        """Return tag."""
        return entry["tag"]

    def _errors(self, entry):
        """Return errors."""
        return entry["errors"]

    def _repository_id(self, entry):
        """Return repository_id."""
        return entry["repository_id"]

    def _event_id(self, entry):
        """Return event_id."""
        return entry["event_id"]

    def _record_id(self, entry):
        """Return record_id."""
        return None

    def _status(self, entry):
        """Return status."""
        return entry["status"]

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "id": self._id(entry),
            "release_id": self._release_id(entry),
            "tag": self._tag(entry),
            "errors": self._errors(entry),
            "repository_id": self._repository_id(entry),
            "event_id": self._event_id(entry),
            "record_id": self._record_id(entry),
            "recid": entry.get("recid"),
            "status": self._status(entry),
        }
