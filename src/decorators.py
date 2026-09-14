import json
from collections.abc import Callable
from functools import wraps

import requests


def handle_db_errors[**P, R](func: Callable[P, R]) -> Callable[P, R | None]:
    """Декоратор для обработки ошибок ввода-вывода."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл не найден.")
            return None
        except requests.exceptions.Timeout:
            print("Ошибка: Таймаут при подключении")
            return None
        except requests.exceptions.ConnectionError:
            print("Ошибка: Не удалось подключиться")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка HTTP: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return None
        except OSError as e:
            print(f"Ошибка при работе с файлом: {e}")
            return False
    return wrapper
