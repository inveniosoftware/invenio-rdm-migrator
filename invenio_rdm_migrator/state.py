# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base state module."""

from abc import ABC
from pathlib import Path
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy_utils.types import JSONType, UUIDType

from .logging import Logger
from .utils import ts


class StateDB:
    """Migration state."""

    def __init__(self, db_dir, validators=None):
        """Constructor.

        :param db_dir: path to sqlite db file.
        """
        # for extra validation that cannot be achieved with SQL constraints
        self.validators = validators or {}
        self.db_dir = Path(db_dir)
        self.db_filepath = self.db_dir / "state.db"
        self._mem_eng = None
        # metadata cannot be initialized lazily since tables is access before mem_eng
        # in any op (get, all, add, etc.)
        self._metadata = sa.MetaData()
        self._initialize_db(self._metadata)  # bind tables to metadata

    @property
    def mem_eng(self):
        """Singleton property for memory engine.

        Lazy loading of data from disk.
        """
        if not self._mem_eng:
            self._mem_eng = sa.create_engine("sqlite:///:memory:")

            self._load_from_disk()

        return self._mem_eng

    @property
    def tables(self):
        """Return the currently registered tables in the metadata."""
        return self._metadata.tables

    def _load_from_disk(self):
        """Loads the database from disk into memory."""
        start = ts(iso=False)
        logger = Logger.get_logger()
        logger.info(f"Loading state from {self.db_filepath}.")

        disk_eng = sa.create_engine(f"sqlite:///{self.db_filepath}")
        self._metadata.create_all(disk_eng)  # create tables if not exist

        self._copy_db(disk_eng, self.mem_eng)  # dump state into in-memory sqlite db

        end = ts(iso=False)
        logger.info("Finished loading state.")
        logger.info(f"State loading took {end-start} seconds.")

    def save(self, filename=None, filepath=None):
        """Save the current in-memory state to disk.

        It will overwrite the loaded db file.
        :param filename: name of the state file, it will be save to db_dir.
        :param filepath: full path, including file name, where to save the state db.
        """
        logger = Logger.get_logger()
        start = ts(iso=False)

        # move current db state to backup
        disk_file = self.db_filepath
        if filepath:  # support overwriting the path
            disk_file = Path(filepath)
        elif filename:  # support overwriting the file name
            disk_file = self.db_dir / filename

        logger.info(f"Dumping state to {disk_file}.")
        backup_file = Path(self.db_filepath.name + ".backup")
        if self.db_filepath.exists():
            self.db_filepath.rename(backup_file)

        # dump state into from sqlite db
        disk_eng = sa.create_engine(f"sqlite:///{disk_file}")
        self._copy_db(self.mem_eng, disk_eng)

        # delete old db (backup)
        backup_file.unlink(missing_ok=True)

        end = ts(iso=False)
        logger.info("Finished dumping state.")
        logger.info(f"State dumping took {end-start} seconds.")

    def get(self, table_name, key_attr, key_value):
        """Query a table by key."""
        table = self.tables[table_name]
        with self.mem_eng.connect() as conn:
            result = conn.execute(
                sa.select(table).where(getattr(table.columns, key_attr) == key_value)
            ).one_or_none()

        return result

    def all(self, table_name):
        """Get all the data from the state.

        :returns: a cursor result.
        """
        table = self.tables[table_name]

        with self.mem_eng.connect() as conn:
            result = conn.execute(sa.select(table))
        return result

    def add(self, table_name, data):
        """Add key,data pair to the state."""
        table = self.tables[table_name]
        self._validate(table, data)
        with self.mem_eng.connect() as conn:
            result = conn.execute(sa.insert(table).values(**data))
            conn.commit()

        assert result.rowcount == 1

    def update(self, table_name, key_attr, key_value, data):
        """Update an entry."""
        table = self.tables[table_name]

        self._validate(table, data)
        with self.mem_eng.connect() as conn:
            result = conn.execute(
                sa.update(table)
                .where(getattr(table.columns, key_attr) == key_value)
                .values(**data)
            )
            conn.commit()

        assert result.rowcount == 1  # the update succeeded

    def _copy_db(cls, src, dest):
        """Copy source database into destination."""
        # sqlalchemy abstraction does not have a backup we need a raw connection
        src_conn = src.raw_connection()
        dst_conn = dest.raw_connection()

        src_conn.backup(dst_conn.connection)

        src_conn.close()
        dst_conn.close()

    def _validate(self, table, data):
        """Validate data for a specific table."""
        validator = self.validators.get(table.name)
        if validator:
            validator.validate(data)

    @classmethod
    def _initialize_db(cls, metadata):
        """Initialize state tables and bind to metadata object."""
        # this registration method is not ideal. It implies a tight coupling between
        # state and which streams can be run, and there is no independence (i.e. running one
        # stream means having all state tables defined rather than only those needed).
        # The tables should be defined per stream (e.g. streams/records/state.py:ParentTable)
        # and then be injected into the state.

        sa.Table(
            "parents",
            metadata,
            sa.Column("recid", sa.String, primary_key=True),
            sa.Column("id", UUIDType, nullable=False, unique=True),
            sa.Column("latest_id", UUIDType),
            # could use default=0, but it could create uncontrolled scenarios
            sa.Column("latest_index", sa.Integer),
            sa.Column("next_draft_id", UUIDType),
            sqlite_autoincrement=False,
        )

        sa.Table(
            "records",
            metadata,
            sa.Column("recid", sa.String, primary_key=True),
            sa.Column("id", UUIDType, nullable=False, unique=True),
            sa.Column("parent_id", UUIDType, nullable=False),
            sa.Column("index", sa.Integer, nullable=False),
            sa.Column("fork_version_id", sa.Integer, nullable=False),
            sa.Column("pids", JSONType, default="{}"),
            sqlite_autoincrement=False,
        )

        sa.Table(
            "communities",
            metadata,
            sa.Column("slug", sa.String, primary_key=True),
            sa.Column("id", UUIDType, unique=True),
            sqlite_autoincrement=False,
        )

        sa.Table(
            "pids",
            metadata,
            sa.Column("pid_value", sa.String, primary_key=True),
            sa.Column("id", sa.Integer, unique=True, nullable=False),
            sa.Column("pid_type", sa.String, nullable=False),
            sa.Column("status", sa.String, nullable=False),
            sa.Column("created", sa.DateTime, nullable=False),
            # keep obj_type since the record needs this key dereferenced
            sa.Column("obj_type", sa.String),
            sqlite_autoincrement=False,
        )

        # e.g. key = max_pid_pk, value = 1_000_000
        sa.Table(
            "global",
            metadata,
            sa.Column("key", sa.String, primary_key=True),
            sa.Column("value", sa.Integer, primary_key=True),
            sqlite_autoincrement=False,
        )


class StateEntity:
    """Helper class to query specific state tables."""

    def __init__(self, state, table_name, pk_attr):
        """Constructor."""
        self.state = state
        self.pk_attr = pk_attr
        self.table_name = table_name

    @classmethod
    def _row_as_dict(cls, row):
        """Transform a Row or LegacyRow into a dict."""
        # needed for backwards compatibility
        row_dict = {}
        if not row:
            return row_dict

        for key, value in row._mapping.items():
            # a better generalization might be wanted, for now we only have
            # string, int, JSON and UUID as column types. the only one cause troubles
            # is uuid, which needs to be stringified.
            if value and isinstance(value, UUID):
                value = str(value)
            row_dict[key] = value

        return row_dict

    def get(self, key):
        """Get a row by key."""
        return self._row_as_dict(self.state.get(self.table_name, self.pk_attr, key))

    def all(self):
        """Get all rows."""
        for row in self.state.all(self.table_name):
            yield self._row_as_dict(row)

    def add(self, key, data):
        """Add data row."""
        self.state.add(self.table_name, {self.pk_attr: key, **data})

    def update(self, key, data):
        """Add data row."""
        self.state.update(
            self.table_name, self.pk_attr, key, {self.pk_attr: key, **data}
        )


class StateValidator(ABC):
    """Validator interface."""

    @classmethod
    def validate(cls, data):
        """Data validation."""
        # abc fails on instantiation, e.g. Test(), since this is a classmethod
        # it will always call the parent, therefore the default is False.
        return False


class STATE:
    """Static class holding a reference to a state query."""

    # implemented this way to avoid having to drill state.global from the
    # runner to the lower level pid_pk()
    # ideally there would be some sort of application context/proxies to access this.
    VALUES = None
    PARENTS = None
    RECORDS = None
    COMMUNITIES = None
    PIDS = None

    @classmethod
    def initialized_state(cls, state_db):
        """Initializes state."""
        cls.PARENTS = StateEntity(state_db, "parents", "recid")
        cls.RECORDS = StateEntity(state_db, "records", "recid")
        cls.COMMUNITIES = StateEntity(state_db, "communities", "slug")
        cls.PIDS = StateEntity(state_db, "pids", "pid_value")
        cls.VALUES = StateEntity(state_db, "global", "key")
