import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from .data import Data
from .processing_strategies import ProcessingStrategy


def _heavy_process_chunk(chunk: list[Data], strategy: ProcessingStrategy) -> list[Data]:
    """Чистая функция для обработки чанка данных в executor.
    Не делает вывода, не обращается к глобальному состоянию.
    """
    return list(strategy.process(iter(chunk)))


class TaskManager:
    """Управляющий компонент задач. Принимает входной поток данных,
    планирует обработку, отправляет часть работы в executor и возвращает
    поток обработанных результатов обратно в приложение.
    """

    def __init__(self, max_workers: int | None = None) -> None:
        """Инициализирует TaskManager с указанным количеством workers."""
        self.max_workers: int | None = max_workers

    def _split_into_chunks(self, data: list[Data], chunk_size: int) -> list[list[Data]]:
        """Разделяет список данных на чанки указанного размера."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    async def process_with_executor(self,data: list[Data],
        strategy: ProcessingStrategy,chunk_size: int = 50,use_processes: bool = False) -> list[Data]:
        """Обрабатывает данные через executor. Разделяет на чанки, запускает
        обработку каждого чанка в executor, собирает результаты.
        Порядок результатов сохраняется.
        """
        if not data:
            return []

        chunks = self._split_into_chunks(data, chunk_size)

        loop = asyncio.get_running_loop()
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            tasks: list[tuple[int, asyncio.Future]] = []
            for i, chunk in enumerate(chunks):
                task = loop.run_in_executor(
                    executor,
                    _heavy_process_chunk,
                    chunk,
                    strategy
                )
                tasks.append((i, task))

            results: list[tuple[int, list[Data]]] = []
            for i, task in tasks:
                chunk_result = await task
                results.append((i, chunk_result))

        results.sort(key=lambda x: x[0])
        all_results: list[Data] = []
        for _, chunk_result in results:
            all_results.extend(chunk_result)

        return all_results
