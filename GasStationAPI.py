import requests
import json
import enum
import datetime


class RequestMethod(enum.Enum):
    GET = "GET"
    POST = "POST"


class GasStationAPI(object):

    def __init__(self, server_address: str, login: str, password: str, date_format: str, timeout: int = 5):
        self.__server_address = server_address
        self.__login = login
        self.__password = password

        self.__date_format = date_format
        self.__time_out = timeout

        self.__token = None
        self.__is_auth = False

    def __request(self, path: str, method: RequestMethod = RequestMethod.POST,
                  params: dict = None,
                  data: dict = None,
                  send_token: bool = True):
        if data is None:
            data = {}
        url = self.__server_address + path
        headers = {"Content-Type": "application/json"}

        if send_token:
            headers["Authorization"] = self.__token

        response = None
        try:
            response = requests.request(str(method.value), url=url, params=params, data=json.dumps(data),
                                        headers=headers, timeout=self.__time_out)

            if not response.ok:
                if response.status_code == 401:
                    self.__is_auth = False
                    print("Время сессии истекло. Авторизуйтесь заного")
                else:
                    print("Ошибка: ", response.status_code)
                    print("Ошибка: ", response.text)
        except requests.exceptions.ReadTimeout:
            print("Превышено время ожидания ответа сервера")

        return response

    def is_auth(self) -> bool:
        return self.__is_auth

    def auth(self) -> bool:
        data = {"login": self.__login, "code": self.__password}
        response = self.__request("auth/", data=data, send_token=False)
        if response and response.ok:
            self.__token = response.headers["Authorization"]
            self.__is_auth = True
            return True
        return False

    def load_orders(self) -> dict or None:
        response = self.__request("orders/items/", method=RequestMethod.GET)
        if response and response.ok:
            return json.loads(response.text)
        return None

    def send_price(self, data: dict) -> bool:
        response = self.__request("price/", data=data)
        return response and response.ok

    def send_configuration(self, data: dict) -> bool:
        response = self.__request("station/", data=data)
        return response and response.ok

    def send_order_volume(self, order_id: int, litre: float):
        response = self.__request("orders/volume/", data={"orderId": order_id, "litre": litre})
        return response and response.ok

    def send_accept_status(self, order_id: int) -> bool:
        return self.__request("orders/accept/?orderId=" + str(order_id), method=RequestMethod.GET).ok

    def send_canceled_status(self, order_id: int, reason: str, extended_order_id, extended_date) -> bool:
        date_string = extended_date.strftime(self.__date_format)
        request_url = "orders/canceled/?orderId=" + str(order_id) + "&reason="+reason + \
                      "&extendedOrderId=" + str(extended_order_id) + "&extendedDate=" + date_string
        response = self.__request(request_url, method=RequestMethod.GET)
        return response and response.ok

    def send_fueling_status(self, order_id: int,) -> bool:
        request_url = "orders/fueling/?orderId=" + str(order_id)
        response = self.__request(request_url, method=RequestMethod.GET)
        return response and response.ok
    # TODO возвращает 502 ошибку

    def send_completed_status(self, order_id: int, litre: float, extended_order_id, extended_date) -> bool:
        date_string = extended_date.strftime(self.__date_format)
        request_url = "orders/completed/?orderId=" + str(order_id) + "&litre=" + str(litre) + \
                      "&extendedOrderId=" + str(extended_order_id) + "&extendedDate=" + date_string
        response = self.__request(request_url, method=RequestMethod.GET)
        return response and response.ok

    # "Columns": {
    # 1: {

    #     // статус ТРК
    #     PumpStatus Status

    #     // кол - во литров
    #     double Litre

    #     // идентификатор заказ в АСУ
    #     string ExtendedId

    #     // идентификатор топлива
    #     string FuelId

    #     // Цена по стелле
    #     Double BasePriceFuel

    #     // сумма заказа
    #     double Sum,

    #     // детализация ошибки string
    #     ErrorMessage
    # },
    # 4: {
    #     .....
    # }
    #     ....N
    # }

    # Free – ТКС свободна
    # Fueling – идет налив
    # Completed – налив завершен иожидает оплаты
    # Unavailable – ошибка на ТРК, ТРК не доступна

    # def post_pay(self, data: str):
    #     request_url = "api/orders/items"
    #     response = self.__request(request_url, method=RequestMethod.GET)
    #     return response and response.ok

    # TODO возвращает 500 ошибку
    # def get_orders_report(self, start_date, end_date, page: int = 0):
    def load_orders_report(self):
        page = 0
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)

        response = self.__request("orders/report/", data={"sdate": start_date.strftime(self.__date_format),
                                                          "edate": end_date.strftime(self.__date_format), "page": page})
        if response and response.ok:
            print("Отчет по заказам получен")
            print(response.text)
            return json.loads(response.text)
        return None

    # TODO возвращает ошибку Method \"GET\" not allowed
    def load_station_status(self, apikey: str) -> dict:
        response = self.__request("station/enable/?apikey=" + apikey, method=RequestMethod.GET)
        if response and response.ok:
            return json.loads(response.text)
