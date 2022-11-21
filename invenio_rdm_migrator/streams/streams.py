# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration streams."""


from datetime import datetime


class Stream:
    """ETL stream."""

    def __init__(self, extract, transform, load):
        """Constructor."""
        self.extract = extract
        self.transform = transform
        self.load = load

    def run(self, cleanup=False):
        """Run ETL stream."""
        start_time = datetime.now()
        print(f"Stream started {start_time.isoformat()}")

        extract_gen = self.extract.run()
        transform_gen = self.transform.run(extract_gen)
        self.load.run(transform_gen, cleanup=cleanup)
        
        end_time = datetime.now()
        print(f"Stream ended {end_time.isoformat()}")

        print(f"Execution time: {end_time - start_time}")
