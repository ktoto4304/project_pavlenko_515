install:
	uv sync
project:
	uv run project2
build:
	uv build
bot:
	uv run project2-bot
test:
	uv run pytest -v