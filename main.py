import time
import datetime

import api_config
from GasStationAPI import GasStationAPI
from GasStation import GasStation, FuelType, Order


def millis():
    return int(round(time.time() * 1000))


def update_orders_list(orders_list_data: []):
    print(orders_list_data)

    for order_data in orders_list_data:
        order_id = order_data["id"]
        if not gas_station.is_order_exist(order_id):
            gas_station.add_order(order_data)


def update_orders_status():
    for order in gas_station.get_orders_list():

        # TEST ORDER 1863
        # if not order.get_id() == 1863:
        #     continue

        if order.get_status() == Order.STATUS_ACCEPT_ORDER:
            # Если цена в заказе и в прайсе не совпадает
            if not gas_station.is_order_price_valid(order):
                api.send_configuration(gas_station.get_configuration())
                continue

            # Если заказ не поддерживается АСУ...
            if not gas_station.is_order_supported(order):
                if api.send_canceled_status(order.get_id(), "Заказ не поддерживается системой", order.get_id(), datetime.date.today()):
                    print("Заказ отменен. Заказ не поддерживается системой")
                    gas_station.remove_order(order.get_id())
                continue

            # Если не удалось изменить статус на ACCEPT
            if not api.send_accept_status(order.get_id()):
                if api.send_canceled_status(order.get_id(), "Сервер отклонил заказ", order.get_id(), datetime.date.today()):
                    print("Заказ отменен. Сервер отклонил заказ")
                    gas_station.remove_order(order.get_id())
                continue

            order.set_status(Order.STATUS_WAITING_REFUELING)

        elif order.get_status() == Order.STATUS_WAITING_REFUELING:
            print("Заказ", order.get_id(), "ожидает заливки")

            if not api.send_fueling_status(order.get_id()):
                if api.send_canceled_status(order.get_id(), "Сервер отклонил заказ", order.get_id(), datetime.date.today()):
                    print("Заказ отменен. Сервер отклонил заказ")
                    gas_station.remove_order(order.get_id())
                continue

            order.set_status(Order.STATUS_FUELING)

        elif order.get_status() == Order.STATUS_FUELING:
            if order.is_completed():
                print("Заказ", order.get_id(), "заправка завершена")
                if api.send_completed_status(order.get_id(), order.get_litre(), order.get_id(), datetime.date.today()):
                    gas_station.remove_order(order.get_id())
                continue

            print("Заказ", order.get_id(), "выполняется. Залито", order.get_current_litre(), "литров из ", order.get_litre())
            api.send_order_volume(order.get_id(), order.get_current_litre())
            # Шаг эмуляции заправки
            order.make_fueling_step()


if __name__ == '__main__':

    gas_station = GasStation(extended_id="00001")

    gas_station.add_column([FuelType.A_80, FuelType.A_92, FuelType.A_95])
    gas_station.add_column([FuelType.A_92_PREMIUM, FuelType.A_95_PREMIUM])

    gas_station.set_price({FuelType.DIESEL: 39.52, FuelType.A_80: 37.12})

    api = GasStationAPI(api_config.SERVER_ADDRESS, api_config.LOGIN, api_config.PASSWORD, api_config.DATE_FORMAT)

    print("Пробуем авторизоваться...")
    if api.auth():
        print("Успешная авторизация")
    else:
        exit(1)

    print("Отсылаем прайс...")
    if api.send_price(gas_station.get_price()):
        print("Прайс передан")

    print("Отсылаем конфигурацию...")
    if api.send_configuration(gas_station.get_configuration()):
        print("Конфигурация передана")

    # Ошибки
    # orders_report = api.load_orders_report()
    # api.load_station_status("")

    # Главный цикл программы
    load_orders_last_time = millis()
    load_orders_interval = 0

    while True:
        cur_time = millis()
        if cur_time - load_orders_last_time > load_orders_interval:
            print("Загружаем список заказов...")
            orders_data = api.load_orders()
            if orders_data:
                load_orders_interval = int(orders_data["nextRetryMs"])

                # Обновляем список заказов
                update_orders_list(orders_data["orders"])

            else:
                load_orders_interval = 5000
            load_orders_last_time = cur_time

            # Обновляем статус заказов
            update_orders_status()
