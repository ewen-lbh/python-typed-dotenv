from __future__ import annotations

__version__ = "1.0.1"
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

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
    return "=".join(rest).lstrip()


def coerce(raw_value: str, syntax: VALUE_FORMATS) -> Any:
    if syntax in (VALUE_FORMATS.yaml_1_1, VALUE_FORMATS.yaml_1_2):
        try:
            from ruamel.yaml import YAML
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Please add support for YAML by installing the 'yaml' extra: \n\n\tpip install typed_dotenv[yaml]"
            )

        yaml = YAML(
            typ="safe",
            # version=("1.1" if syntax == VALUE_FORMATS.yaml_1_1 else "1.2"),
        )

        return yaml.load(f"v: {raw_value}")["v"]

    elif syntax == VALUE_FORMATS.toml:
        try:
            import toml
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Please add support for TOML by installing the 'toml' extra: \n\n\tpip install typed_dotenv[toml]"
            )

        try:
            return toml.loads(f"v = {raw_value}")["v"]
        except toml.decoder.TomlDecodeError as error:
            raise toml.decoder.TomlDecodeError(
                f"Error while parsing {binding.original.string!r}:\n\n\t" + error.msg,
                doc=error.doc,
                pos=error.pos,
            )

    elif syntax == VALUE_FORMATS.json:
        import json

        try:
            return json.loads(f'{{"v": {raw_value}}}')["v"]
        except json.decoder.JSONDecodeError as error:
            raise json.decoder.JSONDecodeError(
                f"Error while parsing {binding.original.string!r}:\n\n\t" + error.msg,
                doc=error.doc,
                pos=error.pos,
            )

    elif syntax == VALUE_FORMATS.python_literal:
        import ast

        return ast.literal_eval(raw_value)

    else:
        raise ValueError(f"Unsupported syntax: {syntax}")


def _parse(filename: Union[str, Path]) -> dict[str, Any]:
    values_format = _get_value_format(Path(filename).read_text())

    bindings = dotenv.parser.parse_stream(Path(filename).open())
    # Remove comments...
    bindings: list[dotenv.parser.Binding] = [b for b in bindings if b.key is not None]
    new_bindings = {}

    for binding in bindings:
        new_bindings[binding.key] = (
            coerce(_get_original_value_repr(binding), values_format)
            if values_format is not None
            else binding.value
        )

    return new_bindings


def load(filename: Union[str, Path] = ".env") -> dict[str, Any]:
    if not Path(filename).exists():
        raise FileNotFoundError(f"File {filename!r} was not found")

    return _parse(filename)


try:
    from pydantic import BaseModel

    def load_into(
        into: BaseModel, filename: Union[str, Path, None] = ".env"
    ) -> BaseModel:
        """
        Load environment variables into a Pydantic model.
        If filename is None, variables will be loaded from the environment and the values' syntax will always be 'YAML 1.2'.
        """

        if filename is None:
            from os import environ

            print(list(environ.keys()))
            print(list(into.__fields__.keys()))
            values = {
                key: coerce(environ[key], syntax=VALUE_FORMATS.yaml_1_2)
                for key in into.__fields__.keys()
            }
            return into(**values)

        if not Path(filename).exists():
            raise FileNotFoundError(f"File {filename!r} was not found")

        return into(**_parse(filename))


except ModuleNotFoundError:
    pass
