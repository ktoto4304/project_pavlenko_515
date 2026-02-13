install:
	uv pip install -e .
project:
	uv run project2
build:
	uv build
lint:
	uv run ruff check .
