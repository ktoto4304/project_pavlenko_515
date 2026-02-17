
from .data import Data, Source


class DataProcessing:
    """Класс для обработки данных о сырье."""

    def __init__(self, name: str = "Обработчик") -> None:
        """Инициализирует обработчик данных с указанным именем."""
        self.name: str = name

    def normalizing(self, data: Source) -> int | None:
        """Нормализует названия сырья в источнике, приводя к нижнему регистру и удаляя пробелы."""
        if not data.data:
            print("Нормализация не требуется, источник пуст")
            return 0
        a = 0
        to_delete: list[int] = []
        for i in range(len(data.data)):
            temp = data.data[i].name
            if not data.data[i]:
                to_delete.append(i)
            data.data[i].name = data.data[i].name.lower().strip()
            if data.data[i].name != temp:
                a += 1
        for i in to_delete:
            data.data.pop(i)
        if a == 0:
            print("Нормализация не требуется")
        else:
            print(f"Успешно нормализовано {a} объекта/ов")
        return None

    def filter_category(self, data: Source, category: str) -> Source:
        """Фильтрует записи в источнике по указанной категории сырья."""
        result = Source(data.name, data.type)
        for i in range(len(data.data)):
            if data.data[i].name == category:
                result.add_data(data.data[i])
        if not result.data:
            print(f"Записей c категорией \"{category}\" не найдено")
        else:
            print(f"Найдено {len(result.data)} записей c категорией \"{category}\"")
        return result

    def filter_price(self, data: Source, min_price: float, max_price: float) -> Source:
        """Фильтрует записи в источнике по диапазону цен."""
        result = Source(data.name, data.type)
        for i in range(len(data.data)):
            if min_price <= data.data[i].price <= max_price:
                result.add_data(data.data[i])
        if not result.data:
            print(f"Записей в диапазоне \"{min_price} - {max_price}\" не найдено")
        else:
            print(f"Найдено {len(result.data)} записей в диапазоне цен \"{min_price} - {max_price}\"")
        return result

    def filter_seller(self, data: Source, seller: str) -> Source:
        """Фильтрует записи в источнике по указанному продавцу."""
        result = Source(data.name, data.type)
        for i in range(len(data.data)):
            if data.data[i].id == seller:
                result.add_data(data.data[i])
        if not result.data:
            print(f"Записей продавца \"{seller}\" не найдено")
        else:
            print(f"Найдено {len(result.data)} записей от продавца \"{seller}\"")
        return result

    def average_price(self, data: Source) -> float:
        """Вычисляет среднюю цену всех записей в источнике."""
        total = 0
        count = 0
        for i in range(len(data.data)):
            total += data.data[i].price
            count += 1
        return total / count if count > 0 else 0

    def word_counter(self, data: Data) -> int:
        """Подсчитывает количество слов в названии сырья."""
        splitted = data.name.split(" ")
        return len(splitted)
