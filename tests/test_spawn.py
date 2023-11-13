import os
import shutil

from pathlib import Path

import pytest

from confspawn.spawn import spawn_write, load_config_value, recipe


@pytest.fixture
def test_dir():
    return Path(__file__).parent.absolute()


@pytest.fixture
def conf_pth(test_dir):
    return test_dir.joinpath("sample_config.toml")


@pytest.fixture
def templ_dir(test_dir):
    return test_dir.joinpath("confs")


@pytest.fixture
def configged_dir(templ_dir):
    conffiged_dir_pth = templ_dir.joinpath("configged")
    yield conffiged_dir_pth
    shutil.rmtree(conffiged_dir_pth)


@pytest.fixture
def deploy_dir(templ_dir):
    deploy_dir_pth = templ_dir.joinpath("deploy")
    yield deploy_dir_pth
    shutil.rmtree(deploy_dir_pth)


@pytest.fixture
def use_dir(test_dir):
    use_dir_pth = test_dir.joinpath("use")
    use_dir_pth.mkdir()
    yield use_dir_pth
    shutil.rmtree(use_dir_pth)


def test_spawn_write(templ_dir, configged_dir, conf_pth):
    spawn_write(conf_pth, templ_dir, configged_dir, env_mode="production")


def test_spawn_write_recurse(templ_dir, configged_dir, conf_pth):
    spawn_write(conf_pth, templ_dir, configged_dir, recurse=True)


@pytest.mark.skipif(
    os.name != "posix", reason="Executable mode undefined outside posix"
)
def test_file_mode(templ_dir, deploy_dir, conf_pth):
    spawn_write(conf_pth, templ_dir, deploy_dir)
    target_script = templ_dir.joinpath("deploy/script.sh")
    assert os.access(target_script, os.X_OK)


def test_recipizer(conf_pth, test_dir, use_dir):
    r_path = test_dir.joinpath("recipe/production/production.spwn.toml")
    recipe(r_path, env_overwrite="production")
    some_path = use_dir.joinpath("production/some.conf")
    assert some_path.exists()
    other_path = use_dir.joinpath("production/other.conf")
    assert other_path.exists()
    s1_path = use_dir.joinpath("production/s1/some.conf")
    assert s1_path.exists()


def test_env_var(conf_pth):
    var = load_config_value(conf_pth, "test.coolenv")

    assert var == "indeedenv"
