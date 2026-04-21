import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class ConcurrentProcessor:
    """Класс конкурентной обработки."""
    def __init__(self, mode: str = "sequential", max_workers: int | None = None):
        self.mode = mode
        self.max_workers = max_workers

    def process_chunks(self, chunks: list[list], worker_func: Callable[[list], list]) -> list:
        if not chunks:
            return []
        if self.mode == "sequential":
            return self._run_sequential(chunks, worker_func)
        if self.mode == "threads":
            return self._run_threads(chunks, worker_func)
        if self.mode == "processes":
            return self._run_processes(chunks, worker_func)
        raise ValueError(f"Неизвестный режим: {self.mode}")

    def _run_sequential(self, chunks: list[list], worker_func: Callable[[list], list]) -> list:
        start = time.time()
        results = []
        for chunk in chunks:
            results.extend(worker_func(chunk))
        print(f"  Последовательная обработка чанков: {time.time() - start:.4f} сек")
        return results

    def _run_threads(self, chunks: list[list], worker_func: Callable[[list], list]) -> list:
        start = time.time()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(worker_func, chunk) for chunk in chunks]
            results = []
            for future in futures:
                result = future.result()
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
        print(f"  Потоковая обработка ({self.max_workers or 'auto'} воркеров): {time.time() - start:.4f} сек")
        return results

    def _run_processes(self, chunks: list[list], worker_func: Callable[[list], list]) -> list:
        start = time.time()
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(worker_func, chunk) for chunk in chunks]
            results = []
            for future in futures:
                result = future.result()
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
        print(f"  Процессная обработка ({self.max_workers or 'auto'} воркеров): {time.time() - start:.4f} сек")
        return results


def split_into_chunks(data: list, chunk_size: int) -> list[list]:
    """Разделяет на чанки."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def measure_execution_time(func: Callable) -> Callable:
    """Замер времени."""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"\n{'='*50}")
        print(f"ВЫПОЛНЕНИЕ: {func.__name__}")
        print(f"Время выполнения: {elapsed:.4f} секунд")
        print(f"{'='*50}")
        return result, elapsed
    return wrapper
