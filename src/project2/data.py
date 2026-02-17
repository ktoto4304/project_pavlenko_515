import uuid


class Data:
    """Класс Единицы памяти."""

    def __init__(self, name: str, price: float, seller: str, note: str = "Нет примечаний") -> None:
        """Инициализирует объект данных о сырье."""
        if type(name) is not str or type(price) is not float or type(seller) is not str:
            raise TypeError()
        if price <= 0:
            raise ValueError()
        self.record_id: str = str(uuid.uuid4())[:8]
        self.note: str = note
        self.name: str = name
        self.price: float = price
        self.id: str = seller

    @property
    def name_display(self) -> str:
        """Возвращает отформатированное название сырья."""
        return f"Тип сырья - {self.name}"

    @property
    def price_display(self) -> str:
        """Возвращает отформатированную цену."""
        return f"Цена за единицу объема - {self.price}"

    @property
    def seller_display(self) -> str:
        """Возвращает отформатированную информацию о продавце."""
        return f"Компания - {self.id}"

    @property
    def record_display(self) -> str:
        """Возвращает отформатированный ID записи."""
        return f"ID записи - {self.record_id}"

    @property
    def note_display(self) -> str:
        """Возвращает отформатированное примечание."""
        if self.note == "Нет примечаний":
            return "Нет примечаний"
        return f"Примечание - {self.note}"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{self.name}: {self.price} (Продавец: {self.id})"

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление объекта."""
        return f"Record_ID = {self.record_id}, Data(name='{self.name}', price={self.price}, seller_id='{self.id}')"


class Source:
    """Класс источника."""

    def __init__(self, name: str = "Неизвестный источник", source_type: str = "test") -> None:
        """Инициализирует источник данных."""
        self.name: str = name
        self.type: str = source_type
        self.data: list[Data] = []

    def add_data(self, data: Data) -> None:
        """Добавляет объект данных в источник."""
        self.data.append(data)

    def delete_data(self, data: Data) -> None:
        """Удаляет объект данных из источника."""
        for j in range(len(self.data)):
            if self.data[j] == data:
                self.data.remove(self.data[j])
                break

    @property
    def return_data(self) -> list[Data]:
        """Возвращает список всех данных и выводит их на печать."""
        for i in range(len(self.data)):
            print(self.data[i])
        return self.data
