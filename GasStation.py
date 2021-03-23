import enum


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


class GasStation(object):

    def __init__(self):
        pass
