.DEFAULT_GOAL := test

sync:
	uv sync --dev

test:
	uv run pytest

build:
	uv build

publish:
	uv publish

clean:
	rm -rf build dist .pytest_cache .coverage htmlcov
