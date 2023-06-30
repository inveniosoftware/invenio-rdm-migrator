# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Kafka extract class."""

"""
# TODO: remove `schema` from debezium message

# TODO: remove from debezium config the following tables:
- pidstore_recid (incremental index)
- transaction
- record_metadata_version
- record_buckets
- pidrelations (all models)
- sipstore (all models)

# TODO: deactivate on Zenodo the integrity check task

# TODO: Implement an extract class that would consume messages from a topic

class KafkaExtract(Extract):

    def __init__(self):
        self.consumer = KafkaConsumer(...)


    def run(self):
        yield self.consumer.consume_one()  # pseudocode, needs to use the actual kafka api
"""
