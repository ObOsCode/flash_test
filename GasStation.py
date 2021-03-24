import enum
from typing import List, Dict


# TODO вместо перечисления сделать статическими полями
class FuelType(enum.Enum):
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

    def __init__(self, column_id: int, fuel_list: List[FuelType]):
        self.__id = column_id
        self.__fuel_list = fuel_list

    def get_id(self) -> int:
        return self.__id

    def get_fuel_list(self) -> List[FuelType]:
        return self.__fuel_list


class GasStation(object):

    next_column_id = 1

    def __init__(self, extended_id: str):
        self.__extended_id = extended_id
        self.__columns_list: List[Column] = []
        self.__price: Dict[str, float] = {}

    def set_price(self, price: Dict[str, float]):
        self.__price = price

    def get_price(self) -> Dict[str, float]:
        return self.__price

    def add_column(self, column_fuel_list: List[FuelType]):
        self.__columns_list.append(Column(GasStation.next_column_id, column_fuel_list))
        GasStation.next_column_id += 1

    def get_configuration(self) -> dict:
        configuration = {"StationExtendedId": self.__extended_id}

        columns_config = {}
        for column in self.__columns_list:
            fuels_conf = []
            for fuel in column.get_fuel_list():
                fuels_conf.append(fuel.value)

            columns_config[column.get_id()] = {"Fuels": fuels_conf}

        configuration["Columns"] = columns_config
        return configuration
