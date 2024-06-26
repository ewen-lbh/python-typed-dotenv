# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.2] - 2024-03-29

### Fixed

- Improve error message with `load_into()` when a environment variable is missing, instead of getting a KeyError, pydantic validation will fail on a None value

## [2.0.1] - 2024-03-29

### Fixed

- Some debuggin print statements slipped through, they were removed

## [2.0.0] - 2024-03-29

### Breaking changes

- Dropped support for Python 3.6 and 3.7

### Added

- Ability to pass `None` as a filename to `load_into()`, to get the environment variables directly from the system environment

### Meta

- Switch from pylint, black and isort to ruff

## [1.0.1] - 2020-07-31

### Fixed

- error while installing the package

## [1.0.0] - 2020-07-31

### Added

- support for yaml 1.1 literals
- support for toml literals
- support for json literals
- support for python literals
- `coerce()`
- `load_into()`
- `load()`

[Unreleased]: https://github.com/ewen-lbh/python-typed-dotenv/compare/v2.0.2...HEAD
[2.0.2]: https://github.com/ewen-lbh/python-typed-dotenv/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/ewen-lbh/python-typed-dotenv/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/ewen-lbh/python-typed-dotenv/compare/v1.0.1...v2.0.0
[1.0.1]: https://github.com/ewen-lbh/python-typed-dotenv/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ewen-lbh/python-typed-dotenv/releases/tag/v1.0.0

[//]: # (C3-2-DKAC:GGH:Rewen-lbh/python-typed-dotenv:Tv{t})
