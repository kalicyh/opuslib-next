.DEFAULT_GOAL := test

sync:
	uv sync --dev

test:
	uv run pytest

bench:
	@echo "Usage: uv run python benchmarks/compare_versions.py --baseline-version <version>"

build:
	uv build

publish:
	uv publish

clean:
	rm -rf build dist .pytest_cache .coverage htmlcov
