class Customer:
    def __init__(self):
        self.__name: str = None
        self.linked_bankaccount_1: BankAccount = None
        self.__composed_wallet: Wallet = None
        self.linked_bankaccount_2: BankAccount = None

