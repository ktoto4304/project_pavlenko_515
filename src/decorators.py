from collections.abc import Callable
from functools import wraps


def handle_db_errors[**P, R](func: Callable[P, R]) -> Callable[P, R | None]:
    """Декоратор для поимки ошибок."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except TypeError as e:
            print(f"Ошибка типов вводимых значений: {e}")
        return None
    return wrapper
