
from .data import Data


class DataProcessing:
    """Класс для обработки данных о сырье."""

    def __init__(self, name: str = "Обработчик") -> None:
        """Инициализирует обработчик данных с указанным именем."""
        self.name: str = name

    def normalizing(self, data_info: list[Data]) -> list[Data]:
        """Нормализует названия сырья, приводя к нижнему регистру и удаляя пробелы."""
        if not data_info:
            print("Нормализация не требуется, источник пуст")
            return []
        a = 0
        to_delete: list[int] = []
        for i in range(len(data_info)):
            temp = data_info[i].name
            if not temp or not temp.strip():
                to_delete.append(i)
            data_info[i].name = data_info[i].name.lower().strip()
            if data_info[i].name != temp:
                a += 1
        for i in reversed(to_delete):
            data_info.pop(i)
        if a == 0:
            print("Нормализация не требуется")
        else:
            print(f"Успешно нормализовано {a} объекта/ов")
        return data_info

    def filter_category(self, data_info: list[Data], category: str) -> list[Data]:
        """Фильтрует записи по указанной категории сырья."""
        result = []
        for i in range(len(data_info)):
            if data_info[i].name == category:
                result.append(data_info[i])
        if not result:
            print(f"Записей c категорией \"{category}\" не найдено")
        else:
            print(f"Найдено {len(result)} записей c категорией \"{category}\"")
        return result

    def filter_price(self, data_info: list[Data], min_price: float, max_price: float) -> list[Data]:
        """Фильтрует записи по диапазону цен."""
        result = []
        for i in range(len(data_info)):
            if min_price <= data_info[i].price <= max_price:
                result.append(data_info[i])
        if not result:
            print(f"Записей в диапазоне \"{min_price} - {max_price}\" не найдено")
        else:
            print(f"Найдено {len(result)} записей в диапазоне цен \"{min_price} - {max_price}\"")
        return result

    def filter_seller(self, data_info: list[Data], seller: str) -> list[Data]:
        """Фильтрует записи по указанному продавцу."""
        result = []
        for i in range(len(data_info)):
            if data_info[i].id == seller:
                result.append(data_info[i])
        if not result:
            print(f"Записей продавца \"{seller}\" не найдено")
        else:
            print(f"Найдено {len(result)} записей от продавца \"{seller}\"")
        return result

    def average_price(self, data_info: list[Data]) -> float:
        """Вычисляет среднюю цену всех записей."""
        total = 0.0
        count = 0
        for i in range(len(data_info)):
            total += data_info[i].price
            count += 1
        return total / count if count > 0 else 0.0

    def word_counter(self, data: Data) -> int:
        """Подсчитывает количество слов в названии сырья."""
        splitted = data.name.split(" ")
        return len(splitted)
