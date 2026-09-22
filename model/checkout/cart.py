from model.product import Product
from model.identity import Customer

class LineItem:
    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("quantity deve ser maior que zero")
        self._product = product
        self._quantity = quantity

    @property
    def product(self):
        return self._product
    
    @property
    def quantity(self):
        return self._quantity

    def with_quantity(self, quantity: int) -> "LineItem":
        # LineItem é imutável: para mudar a quantidade, criamos um novo
        return LineItem(self._product, quantity)

    def subtotal(self) -> float:
        return self._product.final_price() * self._quantity

    def __str__(self):
        return f"{self._product.name} x {self._quantity} = R$ {self._product.final_price():.2f}"

    def __repr__(self):
        return f"LineItem(sku={self._product.sku!r}, qty={self._quantity})"

class Cart:
    def __init__(self, customer: Customer):
        self._customer = customer
        self._items: list[LineItem] = []

    @property
    def customer(self):
        return self._customer
    
    @property
    def items(self):
        return list(self._items)

    def add(self, product: Product, qty: int) -> None:
        if qty <= 0:
            raise ValueError("quantity deve ser maior que zero")
        for i, item in enumerate(self._items):
            if item.product.sku == product.sku:
                # produto já está no carrinho: soma a quantidade em vez de duplicar a linha
                self._items[i] = item.with_quantity(item.quantity + qty)
                return
        self._items.append(LineItem(product, qty))

    def remove(self, sku: str) -> None:
        self._items = [i for i in self._items if str(i.product.sku) != sku]

    def total(self) -> float:
        return sum(i.subtotal() for i in self._items)

    def __str__(self):
        lines = "\n".join(f"  {i}" for i in self._items)
        return f"Cart [{self._customer.name}]\n{lines}\n  Total: R$ {self.total():.2f}"
