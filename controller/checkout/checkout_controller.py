from model.checkout import Order, Cart
from model.identity import Customer
from model.product import Product
from view.checkout.checkout_view import CheckoutView

class CheckoutController:
    def __init__(self, view: CheckoutView):
        self._cart: Cart | None = None
        self._orders: list[Order] = []
        self._view = view

    @property
    def cart(self):
        return self._cart

    @property
    def orders(self):
        return list(self._orders)

    def open_cart(self, customer: Customer) -> None:
        self._cart = Cart(customer)

    def add_item(self, product: Product, qty: int) -> None:
        if not self._cart:
            raise ValueError("No open cart")
        self._cart.add(product, qty)
        self._view.show_cart(self._cart)

    def confirm(self) -> Order | None:
        if not self._cart or not self._cart.items:
            raise ValueError("Cart vazio ou inexistente")
        self._view.show_cart(self._cart)
        if self._view.confirm_prompt():
            print("Obrigado por comprar conosco!") # Deixando minha marca no projeto!
            order = Order(self._cart)
            self._orders.append(order)
            self._view.show_order(order)
            self._cart = None
            return order
        return None

    def list_orders(self) -> None:
        self._view.show_orders(self._orders)

    def find_order(self, order_id: str) -> Order | None:
        for order in self._orders:
            if order.order_id == order_id:
                return order
        return None

    def advance(self, order_id: str) -> Order | None:
        order = self.find_order(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} não encontrada")
        order.advance_status()
        self._view.show_status(order)
        return order