# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""InvenioRDM migration streams runner."""

import logging
from pathlib import Path

import yaml

from ..state import CommunitiesState, ParentsState, PIDMaxPKState, RecordsState
from ..utils import ts
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

        self.tmp_dir = (
            Path(config.get("tmp_dir")) / f"tables-{ts(fmt='%Y-%m-%dT%H%M%S')}"
        )
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self.state_dir = Path(config.get("state_dir"))
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path(config.get("log_dir"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("migration")
        self.logger.setLevel(logging.ERROR)
        fh = logging.FileHandler(self.log_dir / "error.log")
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

        self.db_uri = config.get("db_uri")
        self.streams = []
        self.state = {
            "parents": ParentsState(filepath=self.state_dir / "parents.json"),
            "records": RecordsState(filepath=self.state_dir / "records.json"),
            "communities": CommunitiesState(
                filepath=self.state_dir / "communities.json"
            ),
            "max_pid": PIDMaxPKState(filepath=self.state_dir / "max_pid.json"),
        }

        for definition in stream_definitions:
            if definition.name in config:
                # get will return a None for e.g. files:
                stream_config = config.get(definition.name) or {}
                # merge state objects from stream definition config
                existing_data = stream_config.get("existing_data", {})

                # if loading pass source data dir, else pass tmp to dump new csv files
                stream_data_dir = self.data_dir / definition.name
                extract = None
                transform = None
                if not existing_data:
                    extract = definition.extract_cls(**stream_config.get("extract", {}))
                    transform = definition.transform_cls(
                        **stream_config.get("transform", {})
                    )
                    stream_data_dir = self.tmp_dir / definition.name
                    stream_data_dir.mkdir(parents=True, exist_ok=True)

                self.streams.append(
                    Stream(
                        definition.name,
                        extract,
                        transform,
                        definition.load_cls(
                            db_uri=self.db_uri,
                            data_dir=stream_data_dir,
                            state=self.state,
                            existing_data=existing_data,
                            **stream_config.get("load", {}),
                        ),
                        logger=self.logger,
                    )
                )

    def run(self):
        """Run ETL streams."""
        for stream in self.streams:
            try:
                stream.run()
                # sucessfully finished stream run, now we can dump that stream state
                for name, state in self.state.items():
                    state_file = self.state_dir / f"{name}.json"
                    state.dump(state_file)
            except Exception:
                self.logger.error(f"Stream {stream.name} failed.", exc_info=1)
                continue
