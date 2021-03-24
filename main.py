import api_config
from GasStationAPI import GasStationAPI
from GasStation import GasStation, FuelType


if __name__ == '__main__':

    gas_station = GasStation(extended_id="00001")

    gas_station.add_column([FuelType.A_80, FuelType.A_92])
    gas_station.add_column([FuelType.A_80, FuelType.A_92, FuelType.A_92_PREMIUM])

    gas_station.set_price({FuelType.DIESEL.value: 39.52, FuelType.A_80.value: 37.12})

    api = GasStationAPI(api_config.SERVER_ADDRESS, api_config.LOGIN, api_config.PASSWORD)

    api.auth()
    # api.send_price(gas_station.get_price())
    # api.send_configuration(gas_station.get_configuration())
    #
    # orders = api.get_orders()
    # if orders:
    #     print(orders)
    #     print(orders["nextRetryMs"])

    orders_report = api.get_orders_report()


