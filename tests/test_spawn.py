import os
import shutil

from pathlib import Path

import pytest

from confspawn.spawn import spawn_template, spawn_write, load_env_var


@pytest.fixture
def test_dir():
    return Path(__file__).parent.absolute()


@pytest.fixture
def conf_dir(test_dir):
    return test_dir.joinpath("confs")


@pytest.fixture
def configged_dir(conf_dir):
    conffiged_dir_pth = conf_dir.joinpath("configged")
    yield conffiged_dir_pth
    shutil.rmtree(conffiged_dir_pth)


@pytest.fixture
def deploy_dir(conf_dir):
    deploy_dir_pth = conf_dir.joinpath("deploy")
    yield deploy_dir_pth
    shutil.rmtree(deploy_dir_pth)


def test_spawn_write(conf_dir, configged_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')
    template0 = conf_dir.joinpath('template_conf0.conf')
    template1 = conf_dir.joinpath('template_conf1.yaml')

    zero = spawn_template(sample_conf, template0, "default.nested")
    one = spawn_template(sample_conf, template1, "default.nested")

    spawn_write(sample_conf, conf_dir, target_dir=configged_dir, join_target=False, source_env="default.nested")


@pytest.mark.skipif(os.name != 'posix', reason="Executable mode undefined outside posix")
def test_file_mode(conf_dir, deploy_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')

    spawn_write(sample_conf, "confs", target_dir=deploy_dir, join_target=False, source_env="default.nested")
    target_script = conf_dir.joinpath("deploy/script.sh")
    assert os.access(target_script, os.X_OK)


def test_env_var(conf_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')

    var = load_env_var(sample_conf, "test", "coolenv")

    assert var == "indeedenv"



