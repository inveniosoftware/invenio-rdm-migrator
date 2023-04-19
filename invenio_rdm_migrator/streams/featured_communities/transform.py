# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Invenio RDM migration featured community transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class FeaturedCommunityTransform(Transform):
    """Base class for featured community data transformation."""

    @abstractmethod
    def _featured_community(self, entry):
        """Transform the community."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "featured_community": self._featured_community(entry),
        }


class FeaturedCommunityEntry(Entry):
    """Transform a single featured community entry."""

    @abstractmethod
    def _created(self, entry):
        """Returns the creation date."""
        pass

    @abstractmethod
    def _updated(self, entry):
        """Returns the update date."""
        pass

    @abstractmethod
    def _slug(self, entry):
        """Returns the community slug."""
        pass

    @abstractmethod
    def _start_date(self, entry):
        """Returns the start date."""
        pass

    def transform(self, entry):
        """Transform a featured community entry."""
        return {
            "created": self._created(entry),
            "updated": self._updated(entry),
            "slug": self._slug(entry),
            "start_date": self._start_date(entry),
        }
