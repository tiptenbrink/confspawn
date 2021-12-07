from dynaconf import Dynaconf
from confspawn.dicts import template_replace

__all__ = ['template_replace', 'spawn_template']


def spawn_template(source_settings, template):
    if isinstance(source_settings, str):
        source_settings = Dynaconf(settings_files=[source_settings])
    if isinstance(template, str):
        template = Dynaconf(settings_files=[template])

    new_template = template_replace(template.as_dict(), source_settings)

    return new_template
