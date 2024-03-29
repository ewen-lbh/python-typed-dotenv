import os
from pathlib import Path
import datetime
from pytest import raises
from pydantic import BaseModel

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
        typed_dotenv._get_value_format(
            """
# values: jsoneee
rick=is not moert
            """
        )
    ) is None


def test_detects_no_value_format():
    assert (
        typed_dotenv._get_value_format(
            """
simply=keys
without_any="values: comment"
            """
        )
    ) is None


def test_parses_regular_dotenv():
    result = typed_dotenv._parse(Path(__file__).parent / ".env")
    assert result["STRING"] == "String"
    assert result["SINGLEQUOTED"] == "string (single-quoted)"
    assert result["UNVALID-PYTHON-IDENTIFIER"] == "True"
    assert result["BOOLEAN_FALSE"] == "false"
    assert result["ANOTHER_BOOLEAN_FALSE"] == "False"
    assert result["YES"] == "yes"
    assert result["Yes"] == "Yes"
    assert result["ON"] == "on"
    assert result["OFF"] == "off"
    assert result["NO"] == "no"
    assert result["AN_INT"] == "8593"
    assert result["A_SEXAGECIMAL_INT"] == "12:34:56"
    assert result["A_EXPONENTIAL"] == "54e15"
    assert result["A_FLOAT"] == "544.54"


def test_parses_toml_dotenv():
    result = typed_dotenv._parse(Path(__file__).parent / "toml.env")
    assert result["STRING"] == "String"
    # assert result["SINGLEQUOTED"] == "string (single-quoted)"
    # assert result["UNVALID-PYTHON-IDENTIFIER"] == "True"
    assert result["BOOLEAN_FALSE"] == False
    # assert result["ANOTHER_BOOLEAN_FALSE"] == "False"
    # assert result["YES"] == "yes"
    # assert result["Yes"] == "Yes"
    # assert result["ON"] == "on"
    # assert result["OFF"] == "off"
    # assert result["NO"] == "no"
    assert result["AN_INT"] == 8593
    assert result["A_SEXAGECIMAL_INT"] == datetime.time(12, 34, 56)
    assert result["A_EXPONENTIAL"] == 54e15
    assert result["A_FLOAT"] == 544.54


def test_parses_json_dotenv():
    result = typed_dotenv._parse(Path(__file__).parent / "json.env")
    assert result["STRING"] == "String = test"
    # assert result["SINGLEQUOTED"] == "string (single-quoted)"
    # assert result["UNVALID-PYTHON-IDENTIFIER"] == "True"
    assert result["BOOLEAN_FALSE"] == False
    # assert result["ANOTHER_BOOLEAN_FALSE"] == "False"
    # assert result["YES"] == "yes"
    # assert result["Yes"] == "Yes"
    # assert result["ON"] == "on"
    # assert result["OFF"] == "off"
    # assert result["NO"] == "no"
    assert result["AN_INT"] == 8593
    # assert result["A_SEXAGECIMAL_INT"] == "12:34:56"
    assert result["A_EXPONENTIAL"] == 54e15
    assert result["A_FLOAT"] == 544.54


def test_parses_python_literal_dotenv():
    result = typed_dotenv._parse(Path(__file__).parent / "python_literal.env")
    assert result["STRING"] == "String"
    assert result["SINGLEQUOTED"] == "string (single-quoted)"
    assert result["UNVALID-PYTHON-IDENTIFIER"] == True
    # assert result["BOOLEAN_FALSE"] == False
    assert result["ANOTHER_BOOLEAN_FALSE"] == False
    # assert result["YES"] == "yes"
    # assert result["Yes"] == "Yes"
    # assert result["ON"] == "on"
    # assert result["OFF"] == "off"
    # assert result["NO"] == "no"
    assert result["AN_INT"] == 8593
    # assert result["A_SEXAGECIMAL_INT"] == "12:34:56"
    assert result["A_EXPONENTIAL"] == 54e15
    assert result["A_FLOAT"] == 544.54


def test_parses_yaml_1_2_dotenv():
    result = typed_dotenv._parse(Path(__file__).parent / "yaml_1_2.env")
    assert result["STRING"] == "String"
    assert result["SINGLEQUOTED"] == "string (single-quoted)"
    assert result["UNVALID-PYTHON-IDENTIFIER"] == True
    assert result["BOOLEAN_FALSE"] == False
    assert result["ANOTHER_BOOLEAN_FALSE"] == False
    assert result["YES"] == "yes"
    assert result["Yes"] == "Yes"
    assert result["ON"] == "on"
    assert result["OFF"] == "off"
    assert result["NO"] == "no"
    assert result["AN_INT"] == 8593
    assert result["A_SEXAGECIMAL_INT"] == "12:34:56"
    assert result["A_EXPONENTIAL"] == 54e15
    assert result["A_FLOAT"] == 544.54


def test_raises_exception_when_file_not_found():
    with raises(FileNotFoundError):
        typed_dotenv.load("unexistant_file")

    class A(BaseModel):
        A: str

    with raises(FileNotFoundError):
        typed_dotenv.load_into(A, filename="unexistant_file")


def test_load_into():
    class ADotEnvModel(BaseModel):
        STRING: str
        BOOLEAN_FALSE: bool
        AN_INT: int
        A_SEXAGECIMAL_INT: datetime.time
        A_EXPONENTIAL: int
        A_FLOAT: float

    result = typed_dotenv.load_into(ADotEnvModel, Path(__file__).parent / "toml.env")
    assert isinstance(result, ADotEnvModel)
    assert result.STRING == "String"
    assert result.BOOLEAN_FALSE == False
    assert result.AN_INT == 8593
    assert result.A_SEXAGECIMAL_INT == datetime.time(12, 34, 56)
    assert result.A_EXPONENTIAL == 54e15
    assert result.A_FLOAT == 544.54


def test_load_into_no_filename():
    from os import environ

    class ADotEnvModel(BaseModel):
        STRING: str
        BOOLEAN_FALSE: bool
        AN_INT: int
        A_SEXAGECIMAL_INT: datetime.time
        A_EXPONENTIAL: int
        A_FLOAT: float

    environ["STRING"] = "String"
    environ["BOOLEAN_FALSE"] = "False"
    environ["AN_INT"] = "8593"
    environ["A_SEXAGECIMAL_INT"] = "12:34:56"
    environ["A_EXPONENTIAL"] = "54e15"
    environ["A_FLOAT"] = "544.54"

    print(environ)

    result = typed_dotenv.load_into(ADotEnvModel, filename=None)
    assert isinstance(result, ADotEnvModel)
    assert result.STRING == "String"
    assert result.BOOLEAN_FALSE == False
    assert result.AN_INT == 8593
    assert result.A_SEXAGECIMAL_INT == datetime.time(12, 34, 56)
    assert result.A_EXPONENTIAL == 54e15
    assert result.A_FLOAT == 544.54
