import datetime
import sys

import api_config
from GasStationAPI import GasStationAPI
from GasStation import GasStation, FuelType, Order


def exception_hook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        print("\n *** Программа завершена пользователем ***")
    else:
        sys.__excepthook__(exctype, value, traceback)


def timestamp():
    return int(round(datetime.datetime.now().timestamp() * 1000))


def create_station_configuration() -> dict:
    configuration = {"StationExtendedId": gas_station.get_id()}
    columns_config = {}
    for column in gas_station.get_columns_list():
        columns_config[column.get_id()] = {"Fuels": column.get_fuel_list()}

    configuration["Columns"] = columns_config
    return configuration


def update_orders_list(orders_list_data: []):

    # print(orders_list_data)
    print("Проверяем есть ли новые заказы...")

    new_orders_count = 0

    for order_data in orders_list_data:
        order_id = order_data["id"]
        if not gas_station.is_order_exist(order_id):
            order_type = order_data["orderType"]
            status = order_data["status"]
            contract_id = order_data["ContractId"]
            fuel_id = order_data["fuelId"]
            column_id = order_data["columnId"]
            price_fuel = float(order_data["priceFuel"])
            litre = float(order_data["litre"])
            new_order = Order(order_id, order_type, status, contract_id, fuel_id, column_id, price_fuel, litre)
            gas_station.add_order(new_order)

            print(" Новый заказ: ", new_order)
            new_orders_count += 1

    if new_orders_count == 0:
        print(" Нет новых заказов")


def update_orders_status():

    print("Проверяем статусы заказов...")

    for order in gas_station.get_orders_list():

        # TEST ORDER 1863
        if not order.get_id() == 1862:
            continue

        print("***********************")
        print("Заказ id:", order.get_id())

        if order.get_status() == Order.STATUS_ACCEPT_ORDER:
            print(" Заказ №", order.get_id(), "ожидает подтверждения")

            # Если цены в заказе и в прайсе не совпадают
            if not gas_station.is_order_price_valid(order):
                if api.send_canceled_status(order.get_id(), "Цена в заказе не совпадает с прайсом", order.get_id(), datetime.date.today()):
                    print(" Заказ отменен. Цена в заказе не совпадает с прайсом")
                    gas_station.remove_order(order.get_id())
                # Обновляем прайс на сервере
                api.send_price(gas_station.get_price())
                continue

            # Если заказ не поддерживается
            if not gas_station.is_order_supported(order):
                if api.send_canceled_status(order.get_id(), "Заказ не поддерживается системой", order.get_id(), datetime.date.today()):
                    print(" Заказ отменен. Заказ не поддерживается системой")
                    gas_station.remove_order(order.get_id())
                continue

            # Если не удалось изменить статус на ACCEPT
            if not api.send_accept_status(order.get_id()):
                if api.send_canceled_status(order.get_id(), "Сервер отклонил заказ", order.get_id(), datetime.date.today()):
                    print(" Заказ отменен. Сервер отклонил заказ")
                    gas_station.remove_order(order.get_id())
                continue

            order.set_status(Order.STATUS_WAITING_REFUELING)

        elif order.get_status() == Order.STATUS_WAITING_REFUELING:
            print(" Заказ №", order.get_id(), "ожидает заливки")

            # TODO  Добавить проверку есть ли свободные колонки для выполнения этого заказа !!!!!
            # TODO  Добавить статусы колонкам

            if not api.send_fueling_status(order.get_id()):
                if api.send_canceled_status(order.get_id(), "Сервер отклонил заказ", order.get_id(), datetime.date.today()):
                    print(" Заказ отменен. Сервер отклонил заказ")
                    gas_station.remove_order(order.get_id())
                continue

            order.set_status(Order.STATUS_FUELING)

        elif order.get_status() == Order.STATUS_FUELING:
            if order.is_completed():
                print(" Заправка завершена. Заказ № ", order.get_id(), "выполнен. Отсылаем статус о завершени заказа...")
                if api.send_completed_status(order.get_id(), order.get_litre(), order.get_id(), datetime.date.today()):
                    gas_station.remove_order(order.get_id())
                continue

            print(" Заказ №", order.get_id(), "выполняется. Залито", order.get_current_litre(),
                  "литров из", order.get_litre())

            print("Отсылаем информацию о количестве залитого топлива по заказу", order.get_id(), "...")
            if api.send_order_volume(order.get_id(), order.get_current_litre()):
                print(" Информация по залитому топливу отпралена")

            # Шаг эмуляции заправки
            order.make_fueling_step()


if __name__ == '__main__':

    sys.excepthook = exception_hook

    # Создаем объект модели АЗС
    gas_station = GasStation(extended_id="00001")
    # Добавляем колонки
    gas_station.add_column([FuelType.A_80, FuelType.A_92, FuelType.A_95])
    gas_station.add_column([FuelType.A_92_PREMIUM, FuelType.A_95_PREMIUM])
    # Устанавливаем цены
    gas_station.set_price({FuelType.DIESEL: 39.52, FuelType.A_80: 37.12})

    # Создаем объект для работы с API
    api = GasStationAPI(api_config.SERVER_ADDRESS, api_config.LOGIN, api_config.PASSWORD, api_config.DATE_FORMAT)

    # Ошибки
    # orders_report = api.load_orders_report()
    # api.load_station_status("")

    # Главный цикл программы
    last_step_time = timestamp()
    loop_interval = 0

    while True:
        cur_time = timestamp()
        # Отправляем запрос не чаще loop_interval
        if cur_time - last_step_time > loop_interval:

            # Если не авторизованы отправляем запрос на авторизацию, прайс и конфигурацию
            if not api.is_auth():
                print("Пробуем авторизоваться...")
                if api.auth():
                    print(" Успешная авторизация")
                else:
                    print(" Не удалось авторизоваться")
                    continue

                print("Отсылаем прайс...")
                if api.send_price(gas_station.get_price()):
                    print(" Прайс передан")

                print("Отсылаем конфигурацию...")
                if api.send_configuration(create_station_configuration()):
                    print(" Конфигурация передана")

            print("----------------------------------------------------------------------")
            print("Загружаем список заказов...")
            orders_data = api.load_orders()
            if orders_data:
                print(" Список заказов загружен")
                # Обновляем интервал цикла на полученый от сервера
                loop_interval = int(orders_data["nextRetryMs"])

                # Обновляем список заказов
                update_orders_list(orders_data["orders"])
            else:
                # Если интервал не получен устанавливаем по умолчанию 5000 мс
                loop_interval = 5000
            last_step_time = cur_time

            # Обновляем статус заказов
            update_orders_status()
