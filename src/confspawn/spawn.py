import typing as t
import sys
import os
from functools import reduce
import shutil
from pathlib import Path
import tomli

from jinja2 import BaseLoader, Environment, TemplateNotFound, select_autoescape

__all__ = ['spawn_write', 'load_config_value', 'move_other_files', 'spawn_templates']

if sys.version_info < (3, 9):
    def removeprefix(string: str, prefix: str) -> str:
        if string.startswith(prefix):
            return string[len(prefix):]
        else:
            return string[:]
else:
    def removeprefix(string: str, prefix: str) -> str:
        return string.removeprefix(prefix)


def _get_settings(settings: Path) -> dict:
    with open(settings, "rb") as f:
        toml_dict = tomli.load(f)

    return toml_dict


def load_config_value(settings: Path, var_key: str):
    """Returns the value from a dict loaded from TOML file at the `settings`
    path.

    The `var_key` can use dot-notation to retrieve a nested key (i.e.
    'toplevel.secondlevel.varname').

    Can be used in combination with a print to extract it as an env var.
    See the `confenv` CLI command (`confspawn.cli.config_value`).
    """
    return _deep_get(_get_settings(settings), var_key)


def _deep_get(dic: dict, keys: str, default=None):
    # https://stackoverflow.com/a/46890853/13588694
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
                  keys.split("."), dic)


# Default value can be set using environment variable
# However, this value can be overriden by supplying a prefix value in the specific functions
prefix_env = os.environ.get('CONFSPAWN_PREFIX')
set_prefix_name = prefix_env if prefix_env is not None else "confspawn_"


def _if_to_spawn(pth: Path, prefix_name: str = set_prefix_name):
    return pth.is_file() and pth.name.startswith(prefix_name)


def _get_all_sub_files(pth: Path, recurse=False):
    # rglob("*") goes through all subdirectories and lists all files and directories
    # glob does not recurse
    if recurse:
        globbed = pth.rglob("*")
    else:
        globbed = pth.glob("*")
    return [p for p in globbed]


class SpawnLoader(BaseLoader):
    """`SpawnLoader` serves the same purpose as `jinja2`'s built-in
    `jinja2.loaders.FileSystemLoader`, but only shows the files prefixed with
    'self.prefix_name' as templates."""
    def __init__(
            self,
            searchpath: t.Union[str, os.PathLike],
            encoding: str = "utf-8",
            prefix_name: str = set_prefix_name,
            recurse: bool = False
    ) -> None:

        self.searchpath = Path(searchpath)
        self.encoding = encoding
        self.prefix_name = prefix_name
        self.recurse = recurse

    def get_source(
            self, environment: "Environment", template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        sub_files = _get_all_sub_files(self.searchpath, self.recurse)
        for file_pth in sub_files:
            # We use relative_to to remove the leading parts of the directory file path
            # as_posix for a standardized way to represent the file path
            if _if_to_spawn(file_pth, self.prefix_name) and file_pth.relative_to(self.searchpath
                                                                                 ).as_posix() == template:
                with open(file_pth, mode="rb") as f:
                    contents = f.read().decode(self.encoding)

                mtime = os.path.getmtime(file_pth)

                def uptodate() -> bool:
                    try:
                        return os.path.getmtime(file_pth) == mtime
                    except OSError:
                        return False

                return contents, file_pth.resolve().as_posix(), uptodate
        raise TemplateNotFound(template)

    def list_templates(self) -> t.List[str]:
        template_list = []
        sub_files = _get_all_sub_files(self.searchpath, self.recurse)
        for file_pth in sub_files:
            if _if_to_spawn(file_pth, self.prefix_name):
                template_list.append(file_pth.relative_to(self.searchpath).as_posix())
        return template_list


def _prepare_target(target_path: Path):
    if target_path.exists():
        shutil.rmtree(target_path)
    target_path.mkdir()


def move_other_files(template_path: Path, target_path: Path, recurse: bool = False, prefix_name: str = set_prefix_name):
    """Move all files that are not template files to the other directory.

    The directory must exist.
    """
    for file_pth in _get_all_sub_files(template_path, recurse):
        if file_pth.is_file() and not file_pth.name.startswith(prefix_name):
            shutil.copy(file_pth, target_path)


def spawn_templates(env: Environment, config_dict: dict, target_path: Path, prefix_name: str = set_prefix_name):
    """Move template files and render them with the correct variables."""
    template_names = env.list_templates()
    for templ_name in template_names:
        template = env.get_template(templ_name)
        templ_file = Path(template.filename)
        # Get file mode
        orig_mode = templ_file.stat().st_mode
        mod_template = template.render(config_dict)
        mod_name = removeprefix(templ_file.name, prefix_name)
        mod_path_with_prefix = target_path.joinpath(templ_name)
        mod_path = mod_path_with_prefix.parent.joinpath(mod_name)
        if mod_path.exists():
            raise ValueError(
                f"Modified template file {mod_template} already exists! Ensure no version without {prefix_name}"
                f"is in the main folder.")
        mod_path.parent.mkdir(exist_ok=True, parents=True)
        with open(mod_path, 'x') as f:
            f.write(mod_template)
        # Set file mode
        mod_path.chmod(orig_mode)


def spawn_write(config_path: Path, template_path: Path, target_path: Path, recurse: bool = False,
                prefix_name: str = set_prefix_name):
    """Ensures empty directory exists at target (removing any that exist).

    It then copies non-template files. Finally, it replaces the template
    files with the variables from the config file, after which it also
    moves them to the target with the prefix_name removed. Prefix_name
    defaults to 'confspawn_' but can be set using CONFSPAWN_PREFIX env
    var or directly in this function (the latter takes precedence).
    """

    env = Environment(
        loader=SpawnLoader(template_path, recurse=recurse),
        autoescape=select_autoescape()
    )
    config_dict = _get_settings(config_path)

    _prepare_target(target_path)

    move_other_files(template_path, target_path, recurse, prefix_name)

    spawn_templates(env, config_dict, target_path, prefix_name)

