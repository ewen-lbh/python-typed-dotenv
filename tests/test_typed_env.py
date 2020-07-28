import typed_dotenv
from typed_dotenv import VALUE_FORMATS

def test_detects_and_validates_value_format_comment():
    assert (
        typed_dotenv._get_value_format(
            """
# values: python
THING=test
    """
        )
        == VALUE_FORMATS.python_literal
    )

    assert (
        typed_dotenv._get_value_format(
            """
# values: python-unsafe
THINGIE=testie
"""
        )
        == VALUE_FORMATS.python_eval
    )

    assert (
        typed_dotenv._get_value_format(
            """
# values: yaml 1.1
rick=and-morty
"""
        )
        == VALUE_FORMATS.yaml_1_1
    )

    assert (
        typed_dotenv._get_value_format(
            """
# values: yaml 1.2
rick=adn
"""
        )
        == VALUE_FORMATS.yaml_1_2
    )

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

    assert (
        typed_dotenv._get_value_format(
            """
# valuees: json
rick=is not moert
            """
        )
    ) is None

    assert (
        typed_dotenv._get_value_format(
            """
simply=keys
without_any="values: comment"
            """
        )
    ) is None
