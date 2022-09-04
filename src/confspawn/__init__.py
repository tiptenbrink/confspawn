"""Python package `confspawn` is a simple tool for replacing placeholders in
configuration files for different purposes, such as for Docker Compose or your
PostgreSQL database.

.. include:: ./documentation.md
"""

from confspawn.spawn import spawn_write, load_config_value, move_other_files, spawn_templates
from confspawn.cli import spawner, config_value

__all__ = ['spawn_write', 'load_config_value', 'move_other_files', 'spawn_templates', 'spawner', 'config_value']
