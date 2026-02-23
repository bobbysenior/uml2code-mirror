from abc import ABC, abstractmethod

class IPaymentProcessor(ABC):
    @abstractmethod
    def processPayment(self) -> None:
        pass

