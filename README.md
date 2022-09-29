Installation
------------

```shell
pip install confspawn
```


Usage
-----
Two CLI commands are available, `confspawn` and `confenv`.

```
usage: confenv [-h] -c CONFIG -v VARIABLE

Retrieve configuration value from TOML file.

examples:
confenv -c ./confs/sample_config.toml -v test.coolenv
export TEST_VAR=$(poetry run confenv -c ./confs/sample_config.toml -v test.coolenv)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        File path for your TOML configuration file.
  -v VARIABLE, --variable VARIABLE
                        Variable name to print. For nested keys, use e.g.
                        'toplevel.secondlevel.varname'.
  -e ENV, --env ENV     Useful to specify environment-related modes, i.e.
                        production or development. 'confspawn_env.value' will
                        refer to 'confspawn_env.env.value'. Defaults to
                        'less'.
```

```
usage: confspawn [-h] -c CONFIG -s TEMPLATE -t TARGET [-r] [-p PREFIX]

Easily build configuration files from templates.

examples:
confspawn -c ./config.toml -s ./foo/templates -t /home/me/target

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        File path for your TOML configuration file.
  -s TEMPLATE, --template TEMPLATE
                        Template directory path where your configuration
                        templates are. Other files not indicated by prefix
                        will also be copied over. Does not traverse
                        subdirectories bt default.
  -t TARGET, --target TARGET
                        Target directory path where your files will end up
                        (will be created if none exists, also overwrites
                        previous directory).
  -r, --recurse         Go through template directory recursively.
  -p PREFIX, --prefix PREFIX
                        Prefix that indicates file is a configuration
                        template. Defaults to 'confspawn_' or the value of the
                        CONFSPAWN_PREFIX env var, if set.
  -e ENV, --env ENV     Useful to specify environment-related modes, i.e.
                        production or development. 'confspawn_env.value' will
                        refer to 'confspawn_env.env.value'. Defaults to
                        'less'.
```

```
usage: confrecipe [-h] -r RECIPE [-p PREFIX] [-e ENV]

Build multiple confspawn configurations using a recipe.

examples:
confrecipe -c ./config.toml -s ./foo/templates -t /home/me/target

optional arguments:
  -h, --help            show this help message and exit
  -r RECIPE, --recipe RECIPE
                        File path for your TOML recipe file.
  -p PREFIX, --prefix PREFIX
                        Prefix that indicates file is a configuration
                        template. Defaults to 'confspawn_' or the value of the
                        CONFSPAWN_PREFIX env var, if set.
  -e ENV, --env ENV     Overwrite env set in recipe. Defaults to 'None'.

```

The main entrypoints to use `confspawn` programmatically are `spawn_write()` (corresponds to the `confspawn` command) and `load_config_value()` (corresponds to the `confenv` command). See the documentation for more details.