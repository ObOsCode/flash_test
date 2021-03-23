import config
from GasStationAPI import GasStationAPI
from GasStation import GasStation


if __name__ == '__main__':

    gas_station = GasStation()

    api = GasStationAPI(config.SERVER_ADDRESS, config.LOGIN, config.PASSWORD)

    api.auth()
    api.send_price({"diesel": 39.52, "a80": 37.12})
    # api.send_configuration({})
    api.get_orders()
