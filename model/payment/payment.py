from abc import ABC, abstractmethod
from model.checkout.order import Order
from datetime import datetime
from model.payment.receipt import Receipt

class Payment(ABC):
    @abstractmethod
    def process(self, order: "Order") -> Receipt: ...

    def _make_receipt(self, order: "Order", method: str) -> Receipt:
        return Receipt(
            order_id = order.order_id,
            amount = order.total(),
            method = method,
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        )

class Cash(Payment):
    def __init__(self, tendered: float):
        if tendered < 0:
            raise ValueError("tendered não pode ser negativo")
        self._tendered = tendered

    def process(self, order: "Order") -> Receipt:
        total = order.total()
        if self._tendered < total:
            raise ValueError(
                f"Valor insuficiente: recebido R$ {self._tendered:.2f}, total R$ {total:.2f}"
            )
        change = self._tendered - total
        receipt = self._make_receipt(order, f"Cash (troco: R$ {change:.2f})")
        order.advance_status()
        return receipt

class Card(Payment):
    def __init__(self, last4: str):
        if not last4 or len(last4) != 4 or not last4.isdigit():
            raise ValueError("last4 deve conter exatamente 4 dígitos")
        self._last4 = last4

    def process(self, order: "Order") -> Receipt:
        receipt = self._make_receipt(order, f"Card: **** **** **** {self._last4}")
        order.advance_status()
        return receipt

class Pix(Payment):
    def __init__(self, key: str):
        self._key = key

    # Made with Claude
    def process(self, order: "Order") -> Receipt:
        receipt = self._make_receipt(order, f"Pix: {self._key}")
        order.advance_status()
        return receipt