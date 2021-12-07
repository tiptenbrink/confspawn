from confspawn.spawn import spawn_template, spawn_write


def test_spawn_write():
    zero = spawn_template("sample_config.toml", "./confs/template_conf0.conf", "default.nested")
    one = spawn_template("sample_config.toml", "./confs/template_conf1.yaml", "default.nested")

    spawn_write("sample_config.toml", "confs", source_env="default.nested")
