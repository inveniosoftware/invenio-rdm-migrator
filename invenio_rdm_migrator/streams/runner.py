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
from .cache import ParentsCache, RecordsCache
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
        self.tmp_dir = Path(config.get("tmp_dir"))
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = Path(config.get("cache_dir"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        log_dir = Path(config["log_dir"]) if config.get("log_dir") else None
        self.logger = None
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            self.logger = logging.getLogger("migration")
            self.logger.setLevel(logging.ERROR)
            fh = logging.FileHandler(log_dir / "error.log")
            fh.setLevel(logging.ERROR)
            self.logger.addHandler(fh)

        self.db_uri = config.get("db_uri")
        self.streams = []
        self.cache = {
            "parents": ParentsCache(filepath=self.cache_dir / "parents.json"),
            "records": RecordsCache(filepath=self.cache_dir / "records.json"),
            "communities": {},
        }

        for definition in stream_definitions:
            if definition.name in config:
                stream_config = config.get(definition.name)
                if stream_config is not None:
                    # merge cache objects from stream definition config
                    stream_cache = stream_config.get("load", {}).pop("cache", {})
                    self.cache.update(stream_cache)
                    self.streams.append(
                        Stream(
                            definition.name,
                            definition.extract_cls(**stream_config.get("extract", {})),
                            definition.transform_cls(
                                **stream_config.get("transform", {})
                            ),
                            definition.load_cls(
                                cache=self.cache,
                                tmp_dir=self.tmp_dir,
                                db_uri=self.db_uri,
                                **stream_config.get("load", {}),
                            ),
                            logger=self.logger,
                        )
                    )
                else:
                    # stream is not based on config
                    self.streams.append(
                        Stream(
                            definition.name,
                            definition.extract_cls(),
                            definition.transform_cls(),
                            definition.load_cls(
                                cache=self.cache,
                                tmp_dir=self.tmp_dir,
                                db_uri=self.db_uri,
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
                    if name == "communities":  # FIXME: implement communities cache
                        continue
                    cache_file = self.cache_dir / f"{name}.json"
                    cache.dump(cache_file)
            except Exception:
                self.logger.error(f"Stream {stream.name} failed.", exc_info=1)
                continue
