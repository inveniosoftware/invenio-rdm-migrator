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

from ..utils import ts
from .cache import CommunitiesCache, ParentsCache, PIDMaxPKCache, RecordsCache
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

        self.cache_dir = Path(config.get("cache_dir"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path(config.get("log_dir"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("migration")
        self.logger.setLevel(logging.ERROR)
        fh = logging.FileHandler(self.log_dir / "error.log")
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

        self.db_uri = config.get("db_uri")
        self.streams = []
        self.cache = {
            "parents": ParentsCache(filepath=self.cache_dir / "parents.json"),
            "records": RecordsCache(filepath=self.cache_dir / "records.json"),
            "communities": CommunitiesCache(
                filepath=self.cache_dir / "communities.json"
            ),
            "max_pid": PIDMaxPKCache(filepath=self.cache_dir / "max_pid.json"),
        }

        for definition in stream_definitions:
            if definition.name in config:
                # get will return a None for e.g. files:
                stream_config = config.get(definition.name) or {}
                # merge cache objects from stream definition config
                existing_data = stream_config.get("existing_data", {})

                # if loading pass source data dir, else pass tmp to dump new csv files
                stream_data_dir = self.data_dir
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
                            cache=self.cache,
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
                # sucessfully finished stream run, now we can dump that stream cache
                for name, cache in self.cache.items():
                    cache_file = self.cache_dir / f"{name}.json"
                    cache.dump(cache_file)
            except Exception:
                self.logger.error(f"Stream {stream.name} failed.", exc_info=1)
                continue
