# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""InvenioRDM migration streams runner."""

import yaml

from .streams import Stream


class Runner:
    """ETL streams runner."""

    def _read_config(self, filepath):
        """Read config from file."""
        with open(filepath) as f:
            return yaml.safe_load(f)

    def __init__(self, stream_definitions, config_filepath):
        """Constructor."""
        self.streams = []
        self.cache = {
            # used to keep track of what Parent IDs we've already inserted in the PIDs table.
            # {
            #     '<parent_pid>': {
            #         'id': <generated_parent_uuid>,
            #         'version': {
            #             'latest_index': 'record_index',
            #             'latest_id': 'record id',
            #         }
            # }
            "parent": {},
            "communities": {},
        }
        config = self._read_config(config_filepath)

        for definition in stream_definitions:
            stream_config = config.get(definition.name)
            if stream_config is not None:
                # merge cache objects from stream definition config
                stream_cache = stream_config.get("load", {}).pop("cache", {})
                self.cache.update(stream_cache)
                self.streams.append(
                    Stream(
                        definition.name,
                        definition.extract_cls(**stream_config.get("extract", {})),
                        definition.transform_cls(**stream_config.get("transform", {})),
                        definition.load_cls(
                            **stream_config.get("load", {}), cache=self.cache
                        ),
                    )
                )

    def run(self):
        """Run ETL streams."""
        for stream in self.streams:
            stream.run()
