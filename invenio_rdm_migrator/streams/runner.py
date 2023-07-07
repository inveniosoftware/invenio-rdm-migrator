# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""InvenioRDM migration streams runner."""

from pathlib import Path

import yaml

from ..logging import Logger
from ..state import GLOBAL, State, StateEntity
from .records.state import ParentModelValidator
from .streams import Stream


class Runner:
    """ETL streams runner."""

    def _read_config(self, filepath):
        """Read config from file."""
        with open(filepath) as f:
            return yaml.safe_load(f)

    def __init__(self, stream_definitions, config_filepath):
        """Constructor."""
        config = self._read_config(config_filepath)

        self.data_dir = Path(config.get("data_dir"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tmp_dir = Path(config.get("tmp_dir"))
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self.state_dir = Path(config.get("state_dir"))
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path(config.get("log_dir"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        Logger.initialize(self.log_dir)

        self.db_uri = config.get("db_uri")
        self.streams = []
        self.state = State(
            db_dir=self.state_dir, validators={"parents": ParentModelValidator}
        )

        self.state_entities = {
            "parents": StateEntity(self.state, "parents", "recid"),
            "records": StateEntity(self.state, "records", "recid"),
            "communities": StateEntity(self.state, "communities", "slug"),
            "pids": StateEntity(self.state, "pids", "pid_value"),
        }
        GLOBAL.STATE = StateEntity(self.state, "global", "key")

        # set up secret keys
        GLOBAL.STATE.add(
            "old_secret_key",
            {"value": bytes(config.get("old_secret_key"), "utf-8")},
        )
        GLOBAL.STATE.add(
            "new_secret_key",
            {"value": bytes(config.get("new_secret_key"), "utf-8")},
        )

        # start processing streams
        for definition in stream_definitions:
            if definition.name in config:
                # get will return a None for e.g. files:
                stream_config = config.get(definition.name) or {}
                # merge state objects from stream definition config
                existing_data = stream_config.get("existing_data", {})

                # if loading pass source data dir, else pass tmp to dump new csv files
                data_dir = self.data_dir
                tmp_dir = self.tmp_dir / definition.name
                extract = None
                transform = None
                if not existing_data:
                    extract = definition.extract_cls(**stream_config.get("extract", {}))
                    transform = definition.transform_cls(
                        **stream_config.get("transform", {})
                    )

                self.streams.append(
                    Stream(
                        definition.name,
                        extract,
                        transform,
                        definition.load_cls(
                            db_uri=self.db_uri,
                            data_dir=data_dir,
                            tmp_dir=tmp_dir,
                            state=self.state_entities,
                            existing_data=existing_data,
                            **stream_config.get("load", {}),
                        ),
                    )
                )

    def run(self):
        """Run ETL streams."""
        for stream in self.streams:
            try:
                stream.run()
                # on successful stream run, persist state
                self.state.save(filename=f"{stream.name}.db")
            except Exception:
                Logger.get_logger().exception(
                    f"Stream {stream.name} failed.", exc_info=1
                )
                continue
