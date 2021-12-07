from typing import Union, Optional

from dynaconf import Dynaconf
from confspawn.util import deep_get
from confspawn.read import sub_template


def spawn_template(source_settings: Union[dict, str], template, source_env: Optional[str] = None):
    if isinstance(source_settings, str):
        source_settings = Dynaconf(settings_files=[source_settings])

    source_dict = source_settings.as_dict()
    if source_env is not None:
        source_dict = deep_get(source_dict, source_env)

    with open(template, 'r') as f:
        template_str = f.read()

    new_template = sub_template(template_str, source_dict)

    return new_template



