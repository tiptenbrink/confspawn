import typing as t
import sys
import os
from functools import reduce
import shutil
from pathlib import Path
import tomli

from jinja2 import BaseLoader, Environment, TemplateNotFound, select_autoescape

__all__ = [
    "spawn_write",
    "load_config_value",
    "move_other_files",
    "spawn_templates",
    "recipe",
]

if sys.version_info < (3, 9):

    def removeprefix(string: str, prefix: str) -> str:
        if string.startswith(prefix):
            return string[len(prefix) :]
        else:
            return string[:]

else:

    def removeprefix(string: str, prefix: str) -> str:
        return string.removeprefix(prefix)


def _get_settings(settings: Path, env_mode: str) -> dict:
    with open(settings, "rb") as f:
        toml_dict = tomli.load(f)

    if "confspawn_env" in toml_dict.keys():
        envs = toml_dict["confspawn_env"]
        if isinstance(envs, dict) and env_mode in envs.keys():
            toml_dict["confspawn_env"] = envs[env_mode]
        else:
            toml_dict.pop("confspawn_env")

    return toml_dict


def load_config_value(settings: Path, var_key: str, env_mode: str = "less"):
    """Returns the value from a dict loaded from TOML file at the `settings`
    path.

    The `var_key` can use dot-notation to retrieve a nested key (i.e.
    'toplevel.secondlevel.varname').

    Can be used in combination with a print to extract it as an env var.
    See the `confenv` CLI command (`confspawn.cli.config_value`).
    """
    return _deep_get(_get_settings(settings, env_mode), var_key)


def _deep_get(dic: dict, keys: str, default=None):
    # https://stackoverflow.com/a/46890853/13588694
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dic,
    )


# Default value can be set using environment variable
# However, this value can be overriden by supplying a prefix value in the specific functions
prefix_env = os.environ.get("CONFSPAWN_PREFIX")
set_prefix_name = prefix_env if prefix_env is not None else "confspawn_"


def _if_to_spawn(pth: Path, prefix_name: str = set_prefix_name):
    return pth.is_file() and pth.name.startswith(prefix_name)


def _get_all_sub_files(pth: Path, recurse=False):
    """Get all subfiles and directories.

    If recurse is True, it will also enter subdirectories.
    """
    # rglob("*") goes through all subdirectories and lists all files and directories
    # glob does not recurse
    if recurse:
        globbed = pth.rglob("*")
    else:
        globbed = pth.glob("*")
    return [p for p in globbed]


def _get_all_sub_files_and_rel(
    pth: Path, recurse=False
) -> t.Tuple[t.List[Path], t.List[Path]]:
    """Get all subfiles and zip with relative paths.

    If recurse is True, it will also enter subdirectories.
    """
    # rglob("*") goes through all subdirectories and lists all files and directories
    # glob does not recurse
    if recurse:
        globbed = pth.rglob("*")
    else:
        globbed = pth.glob("*")
    rel_files = []
    abs_files = []

    for p in globbed:
        if p.is_file():
            rel_path = p.relative_to(pth)
            rel_files.append(rel_path)
            abs_files.append(p)

    return abs_files, rel_files


def _merge_paths(
    pth_rec_list: t.List[t.Tuple[Path, bool]]
) -> t.Tuple[t.List[Path], t.List[Path]]:
    """For a list of path, bool pairs, where the bool indicates whether to
    search recursively, see if there is a file conflict.

    Conflicts are checked relative to the source path passed in the
    argument. So a path <path>/some/inner/ will conflict with <other
    path>/some/inner because they would be put at the same target
    location. The returned list contains the absolute files and relative
    paths as tuples.
    """

    files_set: t.Set[Path] = set()
    abs_files = []
    seen_paths = []

    for pth, recurse in pth_rec_list:
        files_set_len = len(files_set)
        if recurse:
            globbed = pth.rglob("*")
        else:
            globbed = pth.glob("*")
        pth_files = []
        for p in globbed:
            if p.is_file():
                rel_path = p.relative_to(pth)
                pth_files.append(rel_path)
                abs_files.append(p)

        files_len = len(pth_files)
        files_set.update(pth_files)
        if len(files_set) != files_set_len + files_len:
            raise ValueError(
                f"There was a path conflict between {', '.join(str(seen_paths))} and {pth}"
            )
        seen_paths.append(pth)

    return abs_files, list(files_set)


class SpawnLoader(BaseLoader):
    """`SpawnLoader` serves the same purpose as `jinja2`'s built-in
    `jinja2.loaders.FileSystemLoader`, but only shows the files prefixed with
    'self.prefix_name' as templates."""

    def __init__(
        self,
        searchpath: t.Union[str, os.PathLike, None] = None,
        encoding: str = "utf-8",
        prefix_name: str = set_prefix_name,
        recurse: bool = False,
        template_locations: t.Optional[t.Tuple[t.List[Path], t.List[Path]]] = None,
    ) -> None:
        if template_locations is not None:
            self.template_locations = template_locations
        elif searchpath is None:
            raise ValueError(
                "Either searchpath or template_locations must be provided!"
            )
        else:
            self.searchpath = Path(searchpath)
        self.encoding = encoding
        self.prefix_name = prefix_name
        self.recurse = recurse
        self.template_locations = template_locations

    def get_source(
        self, environment: "Environment", template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        if self.template_locations is not None:
            sub_files, sub_files_rel = self.template_locations
        else:
            sub_files, sub_files_rel = _get_all_sub_files_and_rel(
                self.searchpath, self.recurse
            )
        for file_pth, rel_path in zip(sub_files, sub_files_rel):
            # We use relative_to to remove the leading parts of the directory file path
            # as_posix for a standardized way to represent the file path
            if (
                _if_to_spawn(file_pth, self.prefix_name)
                and rel_path.as_posix() == template
            ):
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
        if self.template_locations is not None:
            sub_files, sub_files_rel = self.template_locations
        else:
            sub_files, sub_files_rel = _get_all_sub_files_and_rel(
                self.searchpath, self.recurse
            )

        for file_pth, rel_pth in zip(sub_files, sub_files_rel):
            if _if_to_spawn(file_pth, self.prefix_name):
                template_list.append(rel_pth.as_posix())
        return template_list


def _prepare_target(target_path: Path):
    if target_path.exists():
        shutil.rmtree(target_path)
    target_path.mkdir(parents=True)


def move_other_files(
    template_path: Path,
    target_path: Path,
    recurse: bool = False,
    prefix_name: str = set_prefix_name,
    ignore_list: t.Optional[set] = None,
):
    """Move all files that are not template files to the other directory.
    Existing files will be overwritten.

    The directory must exist.
    """
    if ignore_list is None:
        ignore_list = set()

    for file_pth in _get_all_sub_files(template_path, recurse):
        if (
            file_pth.is_file()
            and not file_pth.name.startswith(prefix_name)
            and str(file_pth.resolve()) not in ignore_list
        ):
            # ensure target directory exists
            target_dir = target_path.joinpath(
                file_pth.relative_to(template_path)
            ).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_pth, target_dir)


def move_non_template_file_list(
    file_paths: t.List[Path],
    rel_paths: t.List[Path],
    target_path: Path,
    prefix_name: str = set_prefix_name,
    ignore_list: t.Optional[set] = None,
):
    """Move all files that are not template files to the other directory.

    file_paths should be tuples of absolute paths and paths relative to
    their parent directory (i.e. their target location). Existing files
    will be overwritten. ignore_list should contain the resolved paths
    to ignore.
    """
    if ignore_list is None:
        ignore_list = set()

    # Goes through all subpaths in template_path
    for file_pth, file_pth_rel in zip(file_paths, rel_paths):
        # Files that don't start with prefix and are not ignored are moved
        if (
            file_pth.is_file()
            and not file_pth.name.startswith(prefix_name)
            and str(file_pth.resolve()) not in ignore_list
        ):
            # ensure target directory exists
            target_dir = target_path.joinpath(file_pth_rel).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_pth, target_dir)


def spawn_templates(
    env: Environment,
    config_dict: dict,
    target_path: Path,
    prefix_name: str = set_prefix_name,
):
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
                f"Modified template file {templ_name} already exists! Ensure no version without {prefix_name} "
                f"is in the main folder."
            )
        mod_path.parent.mkdir(exist_ok=True, parents=True)
        with open(mod_path, "x") as f:
            f.write(mod_template)
        # Set file mode
        mod_path.chmod(orig_mode)


def spawn_write(
    config_path: Path,
    template_path: Path,
    target_path: Path,
    recurse: bool = False,
    prefix_name: str = set_prefix_name,
    env_mode: str = "less",
    ignore_list: t.Optional[set] = None,
):
    """Ensures empty directory exists at target (removing any that exist).

    It then copies non-template files. Finally, it replaces the template
    files with the variables from the config file, after which it also
    moves them to the target with the prefix_name removed. Prefix_name
    defaults to 'confspawn_' but can be set using CONFSPAWN_PREFIX env
    var or directly in this function (the latter takes precedence).
    """

    file_paths, rel_paths = _get_all_sub_files_and_rel(template_path, recurse)
    spawn_write_with_paths(
        config_path,
        file_paths,
        rel_paths,
        target_path,
        prefix_name,
        env_mode,
        ignore_list,
    )


def spawn_write_with_paths(
    config_path: Path,
    source_files: t.List[Path],
    source_files_relative: t.List[Path],
    target_path: Path,
    prefix_name: str = set_prefix_name,
    env_mode: str = "less",
    ignore_list: t.Optional[set] = None,
):
    if ignore_list is None:
        ignore_list = set()

    env = Environment(
        loader=SpawnLoader(
            prefix_name=prefix_name,
            template_locations=(source_files, source_files_relative),
        ),
        autoescape=select_autoescape(),
    )
    config_dict = _get_settings(config_path, env_mode)

    _prepare_target(target_path)
    move_non_template_file_list(
        source_files, source_files_relative, target_path, prefix_name, ignore_list
    )

    spawn_templates(env, config_dict, target_path, prefix_name)


def recipe(
    recipe_path: Path,
    prefix_name: str = set_prefix_name,
    env_overwrite: t.Optional[str] = None,
):
    with open(recipe_path, "rb") as f:
        recipe_dict = tomli.load(f)

    if "config" not in recipe_dict:
        raise ValueError(
            "You must specify path for the source 'config'! Like: config = 'config.toml'"
        )

    if (
        "sources" not in recipe_dict
        or not isinstance(recipe_dict["sources"], list)
        or len(recipe_dict["sources"]) == 0
    ):
        raise ValueError(
            "You must include at least one element in the [[sources]] array!"
        )

    config_path = Path(recipe_dict["config"])

    ignore_list = {str(recipe_path.resolve())}

    target_paths: dict = dict()

    for d in recipe_dict["sources"]:
        if "source" not in d or "target" not in d:
            raise ValueError(
                f"'source' and 'target' are required for each recipe {recipe_path!s} array element! They "
                f"must all look like:\n"
                """
                             [[sources]]
                             source = "<template source path>"
                             target = "<target path>"
                             """
            )

        if env_overwrite is None:
            env = d["env"]
        else:
            env = env_overwrite

        recurse = d["recurse"] if "recurse" in d.keys() else False

        s_pth_nm = d["source"]
        t_pth_nm = d["target"]

        spawn_dict = {"src": s_pth_nm, "env": env, "recurse": recurse}

        if t_pth_nm in target_paths:
            t_env = target_paths[t_pth_nm][0]["env"]
            if t_env != env:
                raise ValueError(
                    "When spawning multiple sources to the same target, they must have the same env!"
                )
            target_paths[t_pth_nm].append(spawn_dict)
        else:
            target_paths[t_pth_nm] = [spawn_dict]

    for t_pth_nm in target_paths:
        spawn_dicts = target_paths[t_pth_nm]
        t_pth = Path(t_pth_nm)
        # We checked above if they are the same
        env = spawn_dicts[0]["env"]
        if len(spawn_dicts) > 1:
            src_recs = [(Path(s["src"]), s["recurse"]) for s in spawn_dicts]
            file_paths, rel_paths = _merge_paths(src_recs)

            spawn_write_with_paths(
                config_path,
                file_paths,
                rel_paths,
                t_pth,
                prefix_name,
                env_mode=env,
                ignore_list=ignore_list,
            )
        else:
            s_dct = spawn_dicts[0]
            s_pth = Path(s_dct["src"])
            recurse = s_dct["recurse"]

            spawn_write(
                config_path,
                s_pth,
                t_pth,
                recurse,
                prefix_name,
                env_mode=env,
                ignore_list=ignore_list,
            )
