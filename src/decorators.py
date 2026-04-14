import json
from collections.abc import Callable
from functools import wraps

import requests


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
            print(f"Ошибка при сохранении файла: {e}")
            return False
        return None
    return wrapper
