# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration user transform interfaces."""

from abc import abstractmethod

from ...transform import Entry, Transform


class UserTransform(Transform):
    """Base class for user data transformation."""

    @abstractmethod
    def _user(self, entry):
        """Transform the user."""
        pass

    @abstractmethod
    def _session_activity(self, entry):
        """Transform the session activity."""
        pass

    @abstractmethod
    def _tokens(self, entry):
        """Transform the tokens."""
        pass

    @abstractmethod
    def _applications(self, entry):
        """Transform the applications."""
        pass

    @abstractmethod
    def _oauth(self, entry):
        """Transform the OAuth accounts."""
        pass

    @abstractmethod
    def _identities(self, entry):
        """Transform the identities."""
        pass

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "user": self._user(entry),
            "session_activity": self._session_activity(entry),
            "tokens": self._tokens(entry),
            "applications": self._applications(entry),
            "oauth": self._oauth(entry),
            "identities": self._identities(entry),
        }


class UserEntry(Entry):
    """Transform a single user entry."""

    @abstractmethod
    def _id(self, entry):
        """Returns the user ID."""
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
    def _version_id(self, entry):
        """Returns the version id.

        {Elastic,Open}search will fail with values lower than 1.
        """
        pass

    @abstractmethod
    def _email(self, entry):
        """Returns the email."""
        pass

    @abstractmethod
    def _active(self, entry):
        """Returns if the user is active."""
        pass

    @abstractmethod
    def _password(self, entry):
        """Returns the password."""
        pass

    @abstractmethod
    def _confirmed_at(self, entry):
        """Returns the confirmation date."""
        pass

    @abstractmethod
    def _blocked_at(self, entry):
        """Returns the blocking/inactivation date."""
        pass

    @abstractmethod
    def _verified_at(self, entry):
        """Returns the verification date."""
        pass

    @abstractmethod
    def _username(self, entry):
        """Returns the username."""
        pass

    @abstractmethod
    def _displayname(self, entry):
        """Returns the displayname."""
        pass

    @abstractmethod
    def _profile(self, entry):
        """Returns the profile."""
        pass

    @abstractmethod
    def _preferences(self, entry):
        """Returns the preferences."""
        pass

    @abstractmethod
    def _login_information(self, entry):
        """Returns the login information."""
        pass

    def transform(self, entry):
        """Transform a user single entry."""
        return {
            "id": self._id(entry),
            "created": self._created(entry),
            "updated": self._updated(entry),
            "version_id": self._version_id(entry),
            "email": self._email(entry),
            "active": self._active(entry),
            "password": self._password(entry),
            "confirmed_at": self._confirmed_at(entry),
            "blocked_at": self._blocked_at(entry),
            "verified_at": self._verified_at(entry),
            "username": self._username(entry),
            "displayname": self._displayname(entry),
            "profile": self._profile(entry),
            "preferences": self._preferences(entry),
            "login_information": self._login_information(entry),
        }
