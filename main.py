import time

import api_config
from GasStationAPI import GasStationAPI
from GasStation import GasStation, FuelType


def millis():
    return int(round(time.time() * 1000))


if __name__ == '__main__':

    gas_station = GasStation(extended_id="00001")

    gas_station.add_column([FuelType.A_80, FuelType.A_92])
    gas_station.add_column([FuelType.A_80, FuelType.A_92, FuelType.A_92_PREMIUM])

    gas_station.set_price({FuelType.DIESEL.value: 39.52, FuelType.A_80.value: 37.12})

    api = GasStationAPI(api_config.SERVER_ADDRESS, api_config.LOGIN, api_config.PASSWORD)

    api.auth()
    api.send_price(gas_station.get_price())
    api.send_configuration(gas_station.get_configuration())

    # 500 ошибка
    # orders_report = api.get_orders_report()

    # Главный цикл программы
    get_orders_last_time = millis()
    get_orders_interval = 0

    while True:
        cur_time = millis()
        if cur_time - get_orders_last_time > get_orders_interval:
            print("Загружаем список заказов...")
            orders_data = api.get_orders()
            if orders_data:
                # print("Список заказов загружен:")
                get_orders_interval = int(orders_data["nextRetryMs"])

                orders_list = orders_data["orders"]
                print(orders_list)

            else:
                get_orders_interval = 5000
            get_orders_last_time = cur_time




