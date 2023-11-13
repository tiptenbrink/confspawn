import argparse
import pathlib as p

from confspawn import load_config_value, spawn_write, recipe


def spawner():
    """
    ```shell
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
    """
    cli_name = "confspawn"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Easily build configuration files from templates.\n"
        "\n\n"
        "examples:\n"
        f"{cli_name} -c ./config.toml -s ./foo/templates -t /home/me/target\n",
    )

    config_nm = "config"
    config_help = "File path for your TOML configuration file."
    parser.add_argument("-c", f"--{config_nm}", help=config_help, required=True)

    template_nm = "template"
    template_help = (
        "Template directory path where your configuration templates are. Other files\n"
        "not indicated by prefix will also be copied over. Does not traverse\n"
        "subdirectories bt default."
    )
    parser.add_argument("-s", f"--{template_nm}", help=template_help, required=True)

    target_nm = "target"
    target_help = (
        "Target directory path where your files will end up (will be created if none\n"
        "exists, also overwrites previous directory)."
    )
    parser.add_argument("-t", f"--{target_nm}", help=target_help, required=True)

    recurse_nm = "recurse"
    recurse_help = "Go through template directory recursively."
    parser.add_argument(
        "-r",
        f"--{recurse_nm}",
        help=recurse_help,
        default=False,
        required=False,
        action="store_true",
    )

    prefix_nm = "prefix"
    prefix_default = "confspawn_"
    prefix_help = (
        f"Prefix that indicates file is a configuration template. Defaults to\n"
        f"'{prefix_default}' or the value of the CONFSPAWN_PREFIX env var, if set."
    )
    parser.add_argument("-p", f"--{prefix_nm}", help=prefix_help, required=False)

    env_nm = "env"
    env_default = "less"
    env_help = (
        f"Useful to specify environment-related modes, i.e. production or development. "
        f"'confspawn_env.value' will refer to 'confspawn_env.env.value'. Defaults to"
        f"'{env_default}'."
    )
    parser.add_argument("-e", f"--{env_nm}", help=env_help, required=False)

    config = vars(parser.parse_args())

    config_path = p.Path(config[config_nm])
    template_path = p.Path(config[template_nm])
    target_path = p.Path(config[target_nm])

    if config[prefix_nm] is None:
        spawn_write(
            config_path,
            template_path,
            target_path,
            config[recurse_nm],
            env_mode=config[env_nm],
        )
    else:
        spawn_write(
            config_path,
            template_path,
            target_path,
            config[recurse_nm],
            config[prefix_nm],
            env_mode=config[env_nm],
        )


def config_value():
    """
    ```shell
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
    """
    cli_name = "confenv"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Retrieve configuration value from TOML file.\n"
        "\n\n"
        "examples:\n"
        f"{cli_name} -c ./confs/sample_config.toml -v test.coolenv\n"
        f"export TEST_VAR=$(poetry run confenv -c ./confs/sample_config.toml "
        f"-v test.coolenv)",
    )

    config_nm = "config"
    config_help = "File path for your TOML configuration file."
    parser.add_argument("-c", f"--{config_nm}", help=config_help, required=True)

    var_nm = "variable"
    var_help = "Variable name to print. For nested keys, use e.g. 'toplevel.secondlevel.varname'."
    parser.add_argument("-v", f"--{var_nm}", help=var_help, required=True)

    env_nm = "env"
    env_default = "less"
    env_help = (
        f"Useful to specify environment-related modes, i.e. production or development. "
        f"'confspawn_env.value' will refer to 'confspawn_env.env.value'. Defaults to"
        f"'{env_default}'."
    )
    parser.add_argument("-e", f"--{env_nm}", help=env_help, required=False)

    config = vars(parser.parse_args())

    print(load_config_value(config[config_nm], config[var_nm], config[env_nm]))


def recipizer():
    """
    ```shell
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
    """
    cli_name = "confrecipe"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Build multiple confspawn configurations using a recipe.\n"
        "\n\n"
        "examples:\n"
        f"{cli_name} -c ./config.toml -s ./foo/templates -t /home/me/target\n",
    )

    recipe_nm = "recipe"
    recipe_help = "File path for your TOML recipe file."
    parser.add_argument("-r", f"--{recipe_nm}", help=recipe_help, required=True)

    prefix_nm = "prefix"
    prefix_default = "confspawn_"
    prefix_help = (
        f"Prefix that indicates file is a configuration template. Defaults to\n"
        f"'{prefix_default}' or the value of the CONFSPAWN_PREFIX env var, if set."
    )
    parser.add_argument("-p", f"--{prefix_nm}", help=prefix_help, required=False)

    env_nm = "env"
    env_default = None
    env_help = f"Overwrite env set in recipe. Defaults to '{env_default}'."
    parser.add_argument("-e", f"--{env_nm}", help=env_help, required=False)

    config = vars(parser.parse_args())

    recipe_path = p.Path(config[recipe_nm])

    if config[prefix_nm] is None:
        recipe(recipe_path, env_overwrite=config[env_nm])
    else:
        recipe(recipe_path, config[prefix_nm], config[env_nm])
