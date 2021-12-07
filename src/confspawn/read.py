from dynaconf import Dynaconf

settings = Dynaconf(settings_files=["config.toml"])
template = Dynaconf(settings_files=["compose-template.yaml"])