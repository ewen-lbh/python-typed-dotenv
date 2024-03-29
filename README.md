# typed_dotenv

Parse .env files with types

## Installation

```shell
pip install typed_dotenv
```

To use...

- **[`load_into`](#the-recommended-way-using-pydantics-basemodel-with-load_into)**: `pip install typed_dotenv[pydantic]`
- **YAML literals**: `pip install typed_dotenv[yaml]`
- **TOML literals**: `pip install typed_dotenv[toml]`

## Usage

With the following `.env` file:

```bash
GITHUB_TOKEN="jkjkimnotputtinmygithubpersonaltokeninamodulesexamples"
DEBUG_IN_PRODUCTION=False
```

```python
import typed_dotenv

secrets = typed_dotenv.load(".env")
```

You'll see here that nothing has changed much: `secrets['DEBUG_IN_PRODUCTION']` is still a `str`.

That's because you need to explicitly define what syntax your .env uses.
Add the following at the top of your `.env`:

```bash
# values: python
GITHUB_TOKEN="jkjkimnotputtinmygithubpersonaltokeninamodulesexamples"
DEBUG_IN_PRODUCTION=False
```

Now the following will not raise an assertion error:
```python
import typed_dotenv

secrets = typed_dotenv.load() # ".env" is the default value
assert type(secrets["DEBUG_IN_PRODUCTION"]) is bool
```

We used python-style values, but other syntaxes are available:

- `values: yaml 1.2` to use YAML 1.2 literals<sup>`pip install typed_dotenv[yaml]`</sup>
- `values: yaml 1.1` to use YAML 1.1 literals ([differences from YAML 1.2](https://yaml.readthedocs.io/en/latest/pyyaml.html#defaulting-to-yaml-1-2-support)). **For now, this has the same effect as `values: yaml 1.2`**<sup>`pip install typed_dotenv[yaml]`</sup>
- `values: toml` to use TOML literals: `12:35:24` resolves to a `datetime.time`, etc.<sup>`pip install typed_dotenv[toml]`</sup>
- `values: json` to use JSON literals

Now, up until now, we've only seen how to get those variables into a `dict`.

### The recommended way: using Pydantic's `BaseModel` with `load_into`

This way, you have IDE autcompletion and type checking, and pydantic will raise errors if the value is not of the right type:

```python
from pydantic import BaseModel
import typed_dotenv

class Secrets(BaseModel):
    GITHUB_TOKEN: str
    DEBUG_IN_PRODUCTION: bool

secrets = typed_dotenv.load_into(Secrets, filename="my_dotenv.env")
```

### Production usage without a dotenv file

You can also use `load_into` with `None` as the filename to load variables from the environment:

```python
from pydantic import BaseModel
import typed_dotenv

class Secrets(BaseModel):
    GITHUB_TOKEN: str
    DEBUG_IN_PRODUCTION: bool

secrets = typed_dotenv.load_into(Secrets, filename=None)
```

In that case, the value syntax will always be `YAML 1.2` (we need a format that allows raw strings, since env variables are unquoted).

### Manually coerce from `os.getenv` calls

You might still want to load these values as environment variables, but need to get type coersion. This time, since the value is gotten via `os.getenv`, _typed_dotenv_ does not know the file's contents. The syntax used is thus declared when coercing types:

```python
from os import getenv
import typed_dotenv

print(os.getenv("MY_ENV_VARIABLE"))
print(
    typed_dotenv.coerce(
        os.getenv("MY_ENV_VARIABLE"),
        typed_dotenv.VALUE_FORMATS.python_literal
    )
)
```

You can also make yourself a function to avoid declaring the values' format each time:

```python
def env_coerce(key: str) -> Any:
    return typed_dotenv.coerce(
        os.getenv(key),
        typed_dotenv.VALUE_FORMATS.python_literal
    )
```

And use it like so:

```python
print(env_coerce("MY_ENV_VARIABLE"))
```
