from abc import ABC, abstractmethod
 
class PricingPolicy(ABC):
    @abstractmethod
    def factor(self) -> float: ...

class Normal(PricingPolicy):
    def factor(self):
        return 1.0

class Discount(PricingPolicy):
    # percentage é a fração de desconto, ex: 0.2 = 20% de desconto
    def __init__(self, percentage: float):
        if not (0 <= percentage <= 1):
            raise ValueError("percentage do desconto deve estar entre 0 e 1")
        self._percentage = percentage

    def factor(self):
        # o fator multiplica o preço base: 20% de desconto -> multiplica por 0.8
        return 1.0 - self._percentage