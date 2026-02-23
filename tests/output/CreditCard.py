class CreditCard(Wallet, IPaymentProcessor):
    def __init__(self):
        super().__init__()
        self.__cardNumber: str = None
        self.__coucou: int = None

    def charge(self) -> None:
        pass

    def pay(self, customer: Customer, amount: int) -> None:
        pass

