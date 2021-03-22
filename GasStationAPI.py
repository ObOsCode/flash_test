import requests
import json
import enum


class RequestMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'


class GasStationAPI(object):

    def __init__(self, server_address: str, login: str, password: str):

        self.__server_address = server_address
        self.__login = login
        self.__password = password

        self.__token = None

    def __request(self, path: str, method: RequestMethod = RequestMethod.POST, data: dict = None, send_token: bool = True):
        if data is None:
            data = {}
        url = self.__server_address + path
        headers = {"Content-Type": "application/json"}

        if send_token:
            headers["Authorization"] = self.__token

        # response = requests.post(url, data=json.dumps(data), headers=headers)
        response = requests.request(str(method.name), url=url, data=json.dumps(data), headers=headers)

        if not response.ok:
            if response.status_code == 401:
                print("Время сессии истекло. Авторизуйтесь заного")
            else:
                print("Ощибка: ", response.status_code)
                print("Ощибка: ", response.text)

        return response

    def auth(self):
        data = {"login": self.__login, "code": self.__password}
        response = self.__request("auth/", data=data, send_token=False)
        if response.ok:
            print("Успешная авторизация")
            self.__token = response.headers["Authorization"]

    def send_price(self, data: dict):
        response = self.__request("price/", data=data)
        if response.ok:
            print("Прайс передан")

    def send_configuration(self, data: dict):
        response = self.__request("station/", data=data)
        if response.ok:
            print("Конфигурация передана")

    def get_orders(self):
        response = self.__request("orders/items/", RequestMethod.GET)
        if response.ok:
            print("Список заказов получен")
            print(response.content)
