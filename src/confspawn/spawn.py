from typing import Union, Optional
import sys
from pathlib import Path
import shutil

from dynaconf import Dynaconf
from confspawn.util import deep_get
from confspawn.read import sub_template

if sys.version_info < (3, 9):
    def removeprefix(string: str, prefix: str) -> str:
        if string.startswith(prefix):
            return string[len(prefix):]
        else:
            return string[:]
else:
    def removeprefix(string: str, prefix: str) -> str:
        return string.removeprefix(prefix)


def spawn_template(source_settings: Union[str, Path, Dynaconf, dict], template, source_env: Optional[str] = None):
    if not isinstance(source_settings, Dynaconf) or not isinstance(source_settings, dict):
        source_conf = Dynaconf(settings_files=[source_settings])
    else:
        source_conf = source_settings

    if not isinstance(source_conf, dict):
        source_dict: dict = source_conf.as_dict()
    else:
        source_dict = source_conf

    if source_env is not None:
        source_dict = deep_get(source_dict, source_env)

    if source_dict is None:
        raise ValueError("Unable to properly load source settings, please check paths!")

    with open(template, 'r') as f:
        template_str = f.read()

    new_template = sub_template(template_str, source_dict)

    return new_template


def spawn_write(config_pthstr, template_pthstr, target_dir="configged", join_target=True, source_env=None):
    config_path = Path(config_pthstr)

    db_path = Path(template_pthstr)
    globbed = db_path.glob("*")
    template_files = []
    if join_target:
        target_path = db_path.joinpath(target_dir)
    elif not isinstance(target_dir, Path):
        target_path = Path(target_dir)
    else:
        target_path = target_dir
    if target_path.exists():
        shutil.rmtree(target_path)
    target_path.mkdir()

    for glb in globbed:
        if glb.is_file():
            if glb.name.startswith("template_"):
                template_files.append(glb)
            else:
                shutil.copy(glb, target_path)

    for templ_file in template_files:
        # Get file mode
        orig_mode = templ_file.stat().st_mode
        mod_template = spawn_template(str(config_path), templ_file, source_env)
        mod_name = removeprefix(templ_file.name, "template_")
        mod_path = target_path.joinpath(mod_name)
        if mod_path.exists():
            raise ValueError(
                f"Modified template file {mod_template} already exists! Ensure no version without template_"
                f"is in the main folder.")
        with open(mod_path, 'x') as f:
            f.write(mod_template)
        # Set file mode
        mod_path.chmod(orig_mode)
