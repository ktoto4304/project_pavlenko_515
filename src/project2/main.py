import asyncio

from .app_runner import AppRunner
from .config import get_config


def main() -> None:
    """Запускает приложение в режиме, указанном в конфигурации."""
    config = get_config()
    runner = AppRunner()
    if config.run_mode == "async":
        summary = asyncio.run(runner.run_async())
        runner.print_summary(summary)
    elif config.run_mode == "hybrid":
        summary = asyncio.run(runner.run_hybrid())
        runner.print_summary(summary)
    elif config.run_mode == "sync_delay":
        summary = runner.run_sync_with_delay()
        runner.print_summary(summary)
    else:
        summary = runner.run_sync()
        runner.print_summary(summary)
