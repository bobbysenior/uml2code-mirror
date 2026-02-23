from abc import ABC

class Wallet(ABC):
    def __init__(self):
        self.__amount: double = None

    def addMoney(self) -> None:
        pass

