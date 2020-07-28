__version__ = "0.1.0"
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import dotenv
from parse import parse

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
        parse_results = parse(VALUE_FORMAT_COMMENT_FORMAT, line)
        if parse_results:
            try:
                value_format = [
                    v for v in VALUE_FORMATS if v.value == parse_results[0]
                ][0]
                return value_format
            except IndexError:
                return None
    return None


def load(filename: Union[str, Path] = ".env") -> None:
    if not Path(filename).exists():
        raise FileNotFoundError(f"File {filename!r} was not found")
    dotenv.load_dotenv(filename)
