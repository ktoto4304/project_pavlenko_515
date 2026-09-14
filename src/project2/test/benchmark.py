import io
import os
import sys
import time
from collections.abc import Iterator
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SuppressOutput:
    """Игнорирование ненужного для тестирования вывода."""
    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self.original_stdout


def run_benchmark(mode: str, test_data_size: int = 10000) -> dict[str, Any]:
    """Запуск бенчмарка."""
    from ..config import get_config
    from ..data import Data, Source
    from ..processing_strategies import (
        CompositeStrategy,
        FilterStrategy,
        NormalizationStrategy,
        StatisticsStrategy,
    )
    from .test_data_generator import TestDataGenerator

    class TestSource(Source):
        def __init__(self, name: str, data_list: list):
            self.name = name
            self.type = "test"
            self._data = data_list

        def get_data(self) -> Iterator[Data]:
            return iter(self._data)

    config = get_config()
    config.execution_mode = mode
    config.test_mode = True

    temp_source = TestSource("Temp", [])
    generator = TestDataGenerator(temp_source)
    test_data = generator.generate_data(test_data_size)

    source = TestSource("Тестовый источник (большие данные)", test_data)

    strategy = CompositeStrategy([
        NormalizationStrategy(),
        FilterStrategy(),
        StatisticsStrategy()
    ])

    from ..app import Application

    with SuppressOutput():
        start_time = time.perf_counter()
        app = Application([source], strategy)
        result, exec_time = app.run()
        end_time = time.perf_counter()

    total_time = exec_time if isinstance(exec_time, float) else (end_time - start_time)

    return {
        "mode": mode,
        "data_size": test_data_size,
        "time": total_time,
        "result_count": len(result)
    }


def main():
    """Основная функция теста."""
    data_sizes = [1000, 5000, 10000]

    print("\n" + "="*70)
    print("БЕНЧМАРК ПРОИЗВОДИТЕЛЬНОСТИ")
    print("Сравнение sequential / threads / processes")
    print("="*70)

    all_results = {}

    for size in data_sizes:
        print(f"\n\n{'*'*70}")
        print(f"ТЕСТ С {size} ЗАПИСЯМИ")
        print(f"{'*'*70}")

        results = {}
        for mode in ["sequential", "threads", "processes"]:
            result = run_benchmark(mode, size)
            results[mode] = result
            print(f"\n{mode.upper()}: {result['time']:.4f} сек")
        all_results[size] = results

    print("ИТОГОВОЕ СРАВНЕНИЕ")

    for size in data_sizes:
        print(f"\n--- {size} записей ---")
        results = all_results[size]

        sequential_time = results.get("sequential", {}).get("time", float('inf'))
        threads_time = results.get("threads", {}).get("time", float('inf'))
        processes_time = results.get("processes", {}).get("time", float('inf'))

        if sequential_time != float('inf'):
            print(f"  Sequential: {sequential_time:.4f} сек")
        if threads_time != float('inf'):
            if sequential_time != float('inf') and sequential_time > 0:
                speedup = sequential_time / threads_time
                print(f"  Threads:    {threads_time:.4f} сек (x{speedup:.2f})")
            else:
                print(f"  Threads:    {threads_time:.4f} сек")
        if processes_time != float('inf'):
            if sequential_time != float('inf') and sequential_time > 0:
                speedup = sequential_time / processes_time
                print(f"  Processes:  {processes_time:.4f} сек (x{speedup:.2f})")
            else:
                print(f"  Processes:  {processes_time:.4f} сек")


if __name__ == "__main__":
    main()
