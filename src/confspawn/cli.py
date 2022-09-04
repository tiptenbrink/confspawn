import argparse
import pathlib as p

from confspawn import load_config_value, spawn_write


def spawner():
    """
    ```shell
    usage: confspawn [-h] -c CONFIG -s TEMPLATE -t TARGET [-p PREFIX]

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
                            will also be copied over. Traverses subdirectories
                            recursively.
      -t TARGET, --target TARGET
                            Target directory path where your files will end up
                            (will be created if none exists, also overwrites
                            previous directory).
      -p PREFIX, --prefix PREFIX
                            Prefix that indicates file is a configuration
                            template. Defaults to 'confspawn_' or the value of the
                            CONFSPAWN_PREFIX env var, if set.
    ```
    """
    cli_name = 'confspawn'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="Easily build configuration files from templates.\n"
                                                 "\n\n"
                                                 "examples:\n"
                                                 f"{cli_name} -c ./config.toml -s ./foo/templates -t /home/me/target\n")

    config_nm = 'config'
    config_help = "File path for your TOML configuration file."
    parser.add_argument('-c', f'--{config_nm}', help=config_help, required=True)

    template_nm = 'template'
    template_help = "Template directory path where your configuration templates are. Other files\n" \
                    "not indicated by prefix will also be copied over. Traverses subdirectories\n" \
                    "recursively."
    parser.add_argument('-s', f'--{template_nm}', help=template_help, required=True)

    target_nm = 'target'
    target_help = "Target directory path where your files will end up (will be created if none\n" \
                  "exists, also overwrites previous directory)."
    parser.add_argument('-t', f'--{target_nm}', help=target_help, required=True)

    prefix_nm = 'prefix'
    prefix_default = "confspawn_"
    prefix_help = f"Prefix that indicates file is a configuration template. Defaults to\n" \
                  f"'{prefix_default}' or the value of the CONFSPAWN_PREFIX env var, if set."
    parser.add_argument('-p', f'--{prefix_nm}', help=prefix_help, required=False)

    config = vars(parser.parse_args())

    config_path = p.Path(config[config_nm])
    template_path = p.Path(config[template_nm])
    target_path = p.Path(config[target_nm])

    if config[prefix_nm] is None:
        spawn_write(config_path, template_path, target_path)
    else:
        spawn_write(config_path, template_path, target_path, config[prefix_nm])


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
    ```
    """
    cli_name = 'confenv'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="Retrieve configuration value from TOML file.\n"
                                                 "\n\n"
                                                 "examples:\n"
                                                 f"{cli_name} -c ./confs/sample_config.toml -v test.coolenv\n"
                                                 f"export TEST_VAR=$(poetry run confenv -c ./confs/sample_config.toml "
                                                 f"-v test.coolenv)")

    config_nm = 'config'
    config_help = "File path for your TOML configuration file."
    parser.add_argument('-c', f'--{config_nm}', help=config_help, required=True)

    var_nm = 'variable'
    var_help = "Variable name to print. For nested keys, use e.g. 'toplevel.secondlevel.varname'."
    parser.add_argument('-v', f'--{var_nm}', help=var_help, required=True)

    config = vars(parser.parse_args())

    print(load_config_value(config[config_nm], config[var_nm]))
