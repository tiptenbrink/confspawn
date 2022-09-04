`confspawn` is designed for the following process:

* Create a template source directory, structured as you want your final configuration directory to look. All the files that contain variables that will be transformed based on your universal configuration file, should be prefixed with "confspawn_"
* Run `spawn.spawn_write` on this directory to generate a new directory with all the variables replaced in the configuration files.

To aid with using the universal configuration file in scripts (for example for use in CI/CD), `spawn.load_config_value` is provided to extract the values from a TOML file, for which we have primary support.

Furthermore, the useful underlying methods of `spawn.spawn_write` are also accessible. `spawn.move_other_files` allows moving all non-template files to their target destination, while `spawn.spawn_templates` renders and moves the templates themselves.

## CLI

Two commands are available. `"confspawn"` (`cli.spawner`) activates `spawn.spawn_write` with all options available, while `confenv` (`cli.config_value`) allows printing a variable in a TOML config file.