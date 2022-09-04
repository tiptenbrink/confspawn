"""Python package `confspawn` is a simple tool for replacing placeholders in
configuration files for different purposes, such as for Docker Compose or your
PostgreSQL database.

.. include:: ./documentation.md
"""

from confspawn.spawn import spawn_template, spawn_write, load_config_value
