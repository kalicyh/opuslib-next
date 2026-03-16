# python-opus

Python bindings to the libopus, IETF low-delay audio codec.

## Installation

```bash
pip install opuslib-next
```

## Usage

The API remains compatible with the original `opuslib`, but the package name is now `opuslib_next`.

```python
import opuslib_next
```

## Development

This project now uses a standard `pyproject.toml` and can be managed with `uv`.

```bash
uv sync --dev
uv run pytest
uv build
uv publish
```

If you publish to PyPI, configure credentials first, for example with `UV_PUBLISH_TOKEN` or `uv auth`.

## About the Fork

The original [opuslib](https://github.com/orion-labs/opuslib) is no longer actively maintained. This fork keeps the package working on newer Python versions and accepts fixes.
