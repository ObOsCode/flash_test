from GasStationAPI import GasStationAPI
import config

if __name__ == '__main__':

    print("")

    api = GasStationAPI(config.SERVER_ADDRESS, config.LOGIN, config.PASSWORD)

    api.auth()

    api.send_price({"diesel": 39.52, "a80": 37.12})

    api.send_configuration({})

    api.get_orders()
