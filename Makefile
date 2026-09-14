install:
	uv pip install -e .
project:
	uv run project2
build:
	uv build
lint:
	uv run ruff check src/ --ignore T201
bot:
	uv run project2-bot
test:
	uv run pytest -v