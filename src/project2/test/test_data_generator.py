import json
import random

from ..data import Data, Source


class DataGenerator:
    """Генератор создания тестовых данных."""
    def __init__(self, source: Source):
        self.source = source
        self.commodities = ["нефть", "газ", "золото", "медь", "серебро", "платина", "алюминий", "цинк"]
        self.sellers = ["Норникель", "Газпром", "Лукойл", "Роснефть", "Сургутнефтегаз", "Русал"]

    def generate_data(self, count: int) -> list[Data]:
        data_list = []

        for i in range(count):
            commodity = random.choice(self.commodities)
            price = round(random.uniform(500.0, 10000.0), 2)
            seller = random.choice(self.sellers)
            seller_id = random.randint(1, 100)

            data = Data(
                name=commodity,
                seller_name=seller,
                price=price,
                seller_id=seller_id,
                source=self.source.name if hasattr(self.source, 'name') else str(self.source),
                note=f"Тестовые данные #{i+1}"
            )
            data_list.append(data)

        return data_list

    def save_to_file(self, filename: str, count: int) -> bool:
        data_list = self.generate_data(count)
        serializable_data = []
        for data in data_list:
            serializable_data.append({
                "name": data.name,
                "price": data.price,
                "seller": data.seller.get_name,
                "seller_id": data.seller.get_id,
                "source": data.source,
                "note": data.note
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        print(f"Сгенерировано {count} записей в файл {filename}")
        return True


def create_test_source(filename: str, name: str) -> Source:
    """Создает тестовый источник."""
    from ..sourcefactory import create_source
    return create_source("file", {"filename": filename, "name": name})
