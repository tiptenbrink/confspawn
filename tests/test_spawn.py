import os
import shutil

from pathlib import Path

import pytest

from confspawn.spawn import spawn_write, load_config_value


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

    spawn_write(sample_conf, conf_dir, configged_dir)


def test_spawn_write_recurse(conf_dir, configged_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')

    spawn_write(sample_conf, conf_dir, configged_dir, recurse=True)


@pytest.mark.skipif(os.name != 'posix', reason="Executable mode undefined outside posix")
def test_file_mode(conf_dir, deploy_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')

    spawn_write(sample_conf, conf_dir, deploy_dir)
    target_script = conf_dir.joinpath("deploy/script.sh")
    assert os.access(target_script, os.X_OK)


def test_env_var(conf_dir):
    sample_conf = conf_dir.joinpath('sample_config.toml')

    var = load_config_value(sample_conf, "test.coolenv")

    assert var == "indeedenv"



