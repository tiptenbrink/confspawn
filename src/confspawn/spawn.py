import typing as t
import sys
import os
import shutil
from pathlib import Path
import tomli

from confspawn.util import deep_get
from jinja2 import BaseLoader, Environment, TemplateNotFound, select_autoescape

if sys.version_info < (3, 9):
    def removeprefix(string: str, prefix: str) -> str:
        if string.startswith(prefix):
            return string[len(prefix):]
        else:
            return string[:]
else:
    def removeprefix(string: str, prefix: str) -> str:
        return string.removeprefix(prefix)


def get_settings(settings: Path) -> dict:
    with open(settings, "rb") as f:
        toml_dict = tomli.load(f)

    return toml_dict


def load_config_value(settings: Path, env, var_key):
    settings_dict = deep_get(get_settings(settings), env)
    return settings_dict.get(var_key)


def print_config_value(settings: Path, env, var_key):
    print(load_config_value(settings, env, var_key))


def if_to_spawn(pth: Path):
    return pth.is_file() and pth.name.startswith("confspawn_")


def get_all_sub_files(pth: Path):
    return [p for p in pth.rglob("*")]


class SpawnLoader(BaseLoader):
    def __init__(
            self,
            searchpath: t.Union[str, os.PathLike],
            encoding: str = "utf-8"
    ) -> None:

        self.searchpath = Path(searchpath)
        self.encoding = encoding

    def get_source(
            self, environment: "Environment", template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        sub_files = get_all_sub_files(self.searchpath)
        for file_pth in sub_files:
            if if_to_spawn(file_pth) and file_pth.relative_to(self.searchpath).as_posix() == template:
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
        sub_files = get_all_sub_files(self.searchpath)
        for file_pth in sub_files:
            if if_to_spawn(file_pth):
                template_list.append(file_pth.relative_to(self.searchpath).as_posix())
        return template_list


def spawn_template(config_dict: dict, template_name: str, template_env: Environment):
    template = template_env.get_template(template_name)

    return template.render(config_dict)


def spawn_write(config_path: Path, template_path: Path, target_path: Path):
    """"""
    env = Environment(
        loader=SpawnLoader(template_path),
        autoescape=select_autoescape()
    )
    config_dict = get_settings(config_path)

    template_names = env.list_templates()

    if target_path.exists():
        shutil.rmtree(target_path)
    target_path.mkdir()

    for file_pth in get_all_sub_files(template_path):
        if file_pth.is_file() and not file_pth.name.startswith("confspawn_"):
            shutil.copy(file_pth, target_path)

    for templ_name in template_names:
        template = env.get_template(templ_name)
        templ_file = Path(template.filename)
        # Get file mode
        orig_mode = templ_file.stat().st_mode
        mod_template = spawn_template(config_dict, templ_name, env)
        mod_name = removeprefix(templ_file.name, "confspawn_")
        mod_path = target_path.joinpath(mod_name)
        if mod_path.exists():
            raise ValueError(
                f"Modified template file {mod_template} already exists! Ensure no version without confspawn_"
                f"is in the main folder.")
        with open(mod_path, 'x') as f:
            f.write(mod_template)
        # Set file mode
        mod_path.chmod(orig_mode)

