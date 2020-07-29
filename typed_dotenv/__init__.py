__version__ = "0.1.0"
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

import dotenv
from parse import parse as reverse_format

VALUE_FORMAT_COMMENT_FORMAT = "# values: {}"


class VALUE_FORMATS(str, Enum):
    python_literal = "python"
    python_eval = "python-unsafe"
    yaml_1_1 = "yaml 1.1"
    yaml_1_2 = "yaml 1.2"
    toml = "toml"
    json = "json"


def _get_value_format(contents: str) -> Optional[VALUE_FORMATS]:
    for line in contents.splitlines():
        parse_results = reverse_format(VALUE_FORMAT_COMMENT_FORMAT, line)
        if parse_results:
            try:
                value_format = [
                    v for v in VALUE_FORMATS if v.value == parse_results[0]
                ][0]
                return value_format
            except IndexError:
                return None
    return None


def parse(filename: Union[str, Path]) -> Dict[str, Any]:
    values_format = _get_value_format(Path(filename).read_text())

    bindings = dotenv.parser.parse_stream(Path(filename).open())
    new_bindings = {}

    if values_format in (VALUE_FORMATS.yaml_1_1, VALUE_FORMATS.yaml_1_2):
        try:
            from ruamel.yaml import YAML
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Please add support for YAML by installing the 'yaml' extra: \n\n\tpip install typed_dotenv[yaml]"
            )

        yaml = YAML(
            typ="safe",
            # version=("1.1" if values_format == VALUE_FORMATS.yaml_1_1 else "1.2"),
        )

        for i, binding in enumerate(bindings):
            binding: dotenv.parser.Binding
            new_bindings[binding.key] = yaml.load(f"v: {binding.value}")["v"]
    else:
        for i, binding in enumerate(bindings):
            binding: dotenv.parser.Binding
            new_bindings[binding.key] = binding.value

    return new_bindings


def load(filename: Union[str, Path] = ".env") -> None:
    if not Path(filename).exists():
        raise FileNotFoundError(f"File {filename!r} was not found")
