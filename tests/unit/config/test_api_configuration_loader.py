import os
from pathlib import Path

import pytest

from hargreaves.config import *


def test_load_config_ok():
    config = load_api_config(str(Path(__file__).parent) + "/files/valid.json")

    assert config.username == 'tuser'
    assert config.password == 'tpass'
    assert config.date_of_birth == '010120'
    assert config.secure_number == '123456'


def test_load_config_file_not_found():
    with pytest.raises(ValueError, match=r"Provided secrets file of"):
        load_api_config(str(Path(__file__).parent) + "/not_found.json")


def test_load_config_missing():
    with pytest.raises(ValueError, match=r"^There are null values in the configuration"):
        load_api_config(str(Path(__file__).parent) + "/files/invalid.json")


def test_load_config_bad_structure():
    with pytest.raises(ValueError, match=r"^There are null values in the configuration"):
        load_api_config(str(Path(__file__).parent) + "/files/bad_structure.json")


def test_environment_variables_ok():
    old_environ = dict(os.environ)

    os.environ["HL_USERNAME"] = "tuser2"
    os.environ["HL_PASSWORD"] = "tpass2"
    os.environ["HL_DATE_OF_BIRTH"] = "010130"
    os.environ["HL_SECURE_NUMBER"] = "654321"

    config = load_api_config()

    os.environ.clear()
    os.environ.update(old_environ)

    assert config.username == 'tuser2'
    assert config.password == 'tpass2'
    assert config.date_of_birth == '010130'
    assert config.secure_number == '654321'


def test_environment_variables_missing():
    with pytest.raises(ValueError, match=r"^There are null values in the configuration"):
        load_api_config()
