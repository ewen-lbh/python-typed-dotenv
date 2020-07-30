__version__ = "0.1.0"
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Union

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


def _get_original_value_repr(binding: dotenv.parser.Binding) -> str:
    _key, *rest = binding.original.string.split("=")
    return '='.join(rest).lstrip()


def parse(filename: Union[str, Path]) -> Dict[str, Any]:
    values_format = _get_value_format(Path(filename).read_text())

    bindings = dotenv.parser.parse_stream(Path(filename).open())
    # Remove comments...
    bindings = [b for b in bindings if b.key is not None]
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

        for binding in bindings:
            binding: dotenv.parser.Binding
            new_bindings[binding.key] = yaml.load(
                f"v: {_get_original_value_repr(binding)}"
            )["v"]

    elif values_format == VALUE_FORMATS.toml:
        try:
            import toml
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Please add support for TOML by installing the 'toml' extra: \n\n\tpip install typed_dotenv[toml]"
            )

        for binding in bindings:
            binding: dotenv.parser.Binding
            try:
                new_bindings[binding.key] = toml.loads(
                    f"v = {_get_original_value_repr(binding)}"
                )["v"]
            except toml.decoder.TomlDecodeError as error:
                raise toml.decoder.TomlDecodeError(f"Error while parsing {binding.original.string!r}:\n\n\t" + error.msg, doc=error.doc, pos=error.pos)

    elif values_format == VALUE_FORMATS.json:
        import json

        for binding in bindings:
            binding: dotenv.parser.Binding
            try:
                new_bindings[binding.key] = json.loads(
                    f'{{"v": {_get_original_value_repr(binding)}}}'
                )["v"]
            except json.decoder.JSONDecodeError as error:
                raise json.decoder.JSONDecodeError(f"Error while parsing {binding.original.string!r}:\n\n\t" + error.msg, doc=error.doc, pos=error.pos)

    elif values_format == VALUE_FORMATS.python_literal:
        import ast

        for binding in bindings:
            binding: dotenv.parser.Binding
            new_bindings[binding.key] = ast.literal_eval(
                _get_original_value_repr(binding)
            )

    else:
        for binding in bindings:
            binding: dotenv.parser.Binding
            new_bindings[binding.key] = binding.value

    return new_bindings


def load(filename: Union[str, Path] = ".env") -> Dict[str, Any]:
    if not Path(filename).exists():
        raise FileNotFoundError(f"File {filename!r} was not found")

    return parse(filename)

try:
    from pydantic import BaseModel

    def load_into(into: BaseModel, filename: Union[str, Path] = ".env") -> BaseModel:
        if not Path(filename).exists():
            raise FileNotFoundError(f"File {filename!r} was not found")

        return into(**parse(filename))

except ModuleNotFoundError:
    pass
