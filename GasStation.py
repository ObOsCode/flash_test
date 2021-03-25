from typing import List, Dict


class FuelType(object):
    DIESEL = "diesel"
    DIESEL_PREMIUM = "diesel_premium"
    A_80 = "a80"
    A_92 = "a92"
    A_92_PREMIUM = "a92_premium"
    A_95 = "a95"
    A_95_PREMIUM = "a95_premium"
    A_98 = "a98"
    A_98_PREMIUM = "a98_premium"
    A_100 = "a100"
    PROPANE = "propane"
    METAN = "metan"


class Column(object):

    def __init__(self, column_id: int, fuel_list: List[str]):
        self.__id = column_id
        self.__fuel_list = fuel_list

    def get_id(self) -> int:
        return self.__id

    def get_fuel_list(self) -> List[str]:
        return self.__fuel_list


class Order(object):
    TYPE_MONEY = "Money"
    TYPE_LITERS = "Liters"
    TYPE_FULL_TANK = "FUllTank"

    STATUS_ACCEPT_ORDER = "AcceptOrder"
    STATUS_WAITING_REFUELING = "WaitingRefueling"
    STATUS_FUELING = "Fueling"
    STATUS_EXPIRE = "Expire"

    CONTRACT_ID_INDIVIDUAL = "Individual"
    CONTRACT_ID_CORPORATION = "Corporation"

    # Количество литров заливаемых за один шаг эмуляции
    __FUELING_STEP_LITRE = 0.5
    # Объем полного бака (для эмуляции)
    __FULL_TANK_VOLUME = 45.0

    # TODO передавать не  order_data, а для сделать параметр для каждого атрибута
    def __init__(self, order_data: Dict):
        self.__id = order_data["id"]
        self.__type = order_data["orderType"]
        self.__status = order_data["status"]
        self.__contract_id = order_data["ContractId"]
        self.__fuel_id = order_data["fuelId"]
        self.__column_id = order_data["columnId"]
        self.__price_fuel = float(order_data["priceFuel"])

        # Целевое количество топлива
        if self.__type == Order.TYPE_FULL_TANK:
            self.__litre = Order.__FULL_TANK_VOLUME
        else:
            self.__litre = float(order_data["litre"])

        # Текущее значение залитого топлива
        self.__current_litre = 0

    def get_id(self) -> int:
        return self.__id

    def get_status(self) -> str:
        return self.__status

    def set_status(self, status: str):
        self.__status = status

    def get_fuel_id(self) -> str:
        return self.__fuel_id

    def get_column_id(self) -> int:
        return self.__column_id

    def get_price_fuel(self) -> float:
        return self.__price_fuel

    def get_litre(self) -> float:
        return self.__litre

    def get_current_litre(self) -> float:
        return self.__current_litre

    def is_completed(self) -> bool:
        return self.__current_litre >= self.__litre

    # Делает шаг эмуляции
    def make_fueling_step(self):
        if self.__litre - self.__current_litre < self.__FUELING_STEP_LITRE:
            self.__current_litre = self.__litre
            return
        self.__current_litre += self.__FUELING_STEP_LITRE


class GasStation(object):
    next_column_id = 1

    def __init__(self, extended_id: str):
        self.__extended_id = extended_id
        self.__columns_list: List[Column] = []
        self.__orders_list: List[Order] = []
        self.__price: Dict[str, float] = {}

    def set_price(self, price: Dict[str, float]):
        self.__price = price

    def get_price(self) -> Dict[str, float]:
        return self.__price

    def get_orders_list(self) -> List[Order]:
        return self.__orders_list

    def add_order(self, order_data: Dict):
        self.__orders_list.append(Order(order_data))

    def remove_order(self, order_id: int):
        for order in self.__orders_list:
            if order.get_id() == order_id:
                self.__orders_list.remove(order)
                return

    def is_order_exist(self, order_id: int) -> bool:
        return any(order.get_id() == order_id for order in self.__orders_list)

    def is_order_price_valid(self, order: Order) -> bool:
        # Проверка на соответствие цены в прайсе и в заказе
        return self.__price[order.get_fuel_id()] == order.get_price_fuel()

    def is_order_supported(self, order: Order) -> bool:
        # Если есть колонка с таким id как в заказе и в ней есть топливо как в заказе
        return any(order.get_column_id() == column.get_id() and order.get_fuel_id() in column.get_fuel_list() for column in self.__columns_list)

    def add_column(self, column_fuel_list: List[str]):
        self.__columns_list.append(Column(GasStation.next_column_id, column_fuel_list))
        GasStation.next_column_id += 1

    # Конфигурацию лучше формировать функцией снаружи
    def get_configuration(self) -> dict:
        configuration = {"StationExtendedId": self.__extended_id}
        columns_config = {}
        for column in self.__columns_list:
            columns_config[column.get_id()] = {"Fuels": column.get_fuel_list()}

        configuration["Columns"] = columns_config

        return configuration
