import os
from pathlib import Path

from pytest import raises

import typed_dotenv
from typed_dotenv import VALUE_FORMATS


def test_detects_value_format_python_literal():
    assert (
        typed_dotenv._get_value_format(
            """
# values: python
THING=test
    """
        )
        == VALUE_FORMATS.python_literal
    )


def test_detects_value_format_python_eval():
    assert (
        typed_dotenv._get_value_format(
            """
# values: python-unsafe
THINGIE=testie
"""
        )
        == VALUE_FORMATS.python_eval
    )


def test_detects_value_format_yaml_1_1():
    assert (
        typed_dotenv._get_value_format(
            """
# values: yaml 1.1
rick=and-morty
"""
        )
        == VALUE_FORMATS.yaml_1_1
    )


def test_detects_value_format_yaml_1_2():
    assert (
        typed_dotenv._get_value_format(
            """
# values: yaml 1.2
rick=adn
"""
        )
        == VALUE_FORMATS.yaml_1_2
    )


def test_detects_value_format_toml():
    assert (
        typed_dotenv._get_value_format(
            """
# values: toml
rick=true
but_not=True
"""
        )
        == VALUE_FORMATS.toml
    )


def test_detects_value_format_json():
    assert (
        typed_dotenv._get_value_format(
            """
# values: json
rick="morty"
mort_=is an error
"""
        )
        == VALUE_FORMATS.json
    )


def test_detects_value_format_invalid():
    assert (
        (
            typed_dotenv._get_value_format(
                """
# values: jsoneee
rick=is not moert
            """
            )
        )
        is None
    )


def test_detects_no_value_format():
    assert (
        (
            typed_dotenv._get_value_format(
                """
simply=keys
without_any="values: comment"
            """
            )
        )
        is None
    )


def test_parses_regular_dotenv():
    typed_dotenv.load(Path(__file__).parent / ".env")
    assert os.getenv("STRING") == "String"
    assert os.getenv("SINGLEQUOTED") == "string (single-quoted)"
    assert os.getenv("UNVALID-PYTHON-IDENTIFIER") == "True"
    assert os.getenv("BOOLEAN_FALSE") == "false"
    assert os.getenv("ANOTHER_BOOLEAN_FALSE") == "False"
    assert os.getenv("YES") == "yes"
    assert os.getenv("ON") == "on"
    assert os.getenv("OFF") == "off"
    assert os.getenv("NO") == "no"

def test_raises_exception_when_file_not_found():
    with raises(FileNotFoundError):
        typed_dotenv.load("unexistant_file")
