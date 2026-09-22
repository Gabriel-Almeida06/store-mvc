"""
Store MVC — ponto de entrada da aplicação.

Une os cinco domínios (identidade, produto, inventário, checkout, pagamento)
numa CLI simples com três fluxos:

    customer_flow      -> login/cadastro, browsing, carrinho, checkout, pagamento
    manager_flow        -> cadastrar produto, estocar, política de preço, relatório
    fulfillment_flow     -> listar orders, avançar status
"""

from model.product import Normal, Discount, PricingPolicy
from model.payment import Payment

from view.identity.customer_view import CustomerView
from view.product.product_view import ProductView
from view.inventory.inventory_view import InventoryView
from view.checkout.checkout_view import CheckoutView
from view.payment.payment_view import PaymentView

from controller.identity.customer_controller import CustomerController
from controller.product.product_controller import ProductController
from controller.inventory.inventory_controller import InventoryController
from controller.checkout.checkout_controller import CheckoutController
from controller.payment.payment_controller import PaymentController


class Store:
    """Amarra todos os controllers/views num único lugar (o "app")."""

    def __init__(self):
        self.customer_ctrl = CustomerController(CustomerView())
        self.product_ctrl = ProductController(ProductView())
        self.inventory_ctrl = InventoryController(InventoryView())
        self.checkout_ctrl = CheckoutController(CheckoutView())
        self.payment_ctrl = PaymentController(PaymentView())


# ---------------------------------------------------------------------------
# Helpers de menu
# ---------------------------------------------------------------------------

def _prompt_menu(title: str, options: list[tuple[str, str]]) -> str:
    print(f"\n== {title} ==")
    for key, label in options:
        print(f"  [{key}] {label}")
    return input("Escolha: ").strip()


# ---------------------------------------------------------------------------
# customer_flow -> login/cadastro, browsing, carrinho, checkout, pagamento
# ---------------------------------------------------------------------------

def customer_flow(store: Store) -> None:
    print("\n--- Área do Cliente ---")
    choice = _prompt_menu("Identificação", [
        ("1", "Login (buscar por ID/email)"),
        ("2", "Cadastrar novo cliente"),
        ("0", "Voltar"),
    ])

    customer = None
    if choice == "1":
        customer_id = input("Seu ID/email: ").strip()
        customer = store.customer_ctrl.find(customer_id)
        if not customer:
            print("Cliente não encontrado.")
            return
    elif choice == "2":
        try:
            customer = store.customer_ctrl.register()
        except ValueError as e:
            print(f"Erro ao cadastrar: {e}")
            return
    else:
        return

    store.checkout_ctrl.open_cart(customer)

    while True:
        choice = _prompt_menu("Loja", [
            ("1", "Ver produtos"),
            ("2", "Adicionar produto ao carrinho"),
            ("3", "Ver carrinho"),
            ("4", "Remover item do carrinho"),
            ("5", "Fechar pedido (checkout)"),
            ("0", "Voltar"),
        ])

        if choice == "1":
            store.product_ctrl.list_all()

        elif choice == "2":
            product = store.product_ctrl.prompt_choice()
            if product is None:
                print("Nenhum produto cadastrado ainda.")
                continue
            try:
                qty = int(input("Quantidade: "))
                store.checkout_ctrl.add_item(product, qty)
            except ValueError as e:
                print(f"Erro: {e}")

        elif choice == "3":
            print(store.checkout_ctrl.cart)

        elif choice == "4":
            sku = input("SKU a remover: ").strip()
            store.checkout_ctrl.cart.remove(sku)
            print(store.checkout_ctrl.cart)

        elif choice == "5":
            try:
                order = store.checkout_ctrl.confirm()
            except ValueError as e:
                print(f"Erro: {e}")
                continue
            if order is None:
                print("Pedido cancelado.")
                continue

            store.payment_ctrl.prompt_method(order.total())
            try:
                store.payment_ctrl.process(order)
                customer.add_points(int(order.total()))
            except ValueError as e:
                print(f"Erro no pagamento: {e}")
            store.checkout_ctrl.open_cart(customer)

        elif choice == "0":
            return
        else:
            print("Opção inválida.")


# ---------------------------------------------------------------------------
# manager_flow -> cadastrar produto, estocar, política de preço, relatório
# ---------------------------------------------------------------------------

def manager_flow(store: Store) -> None:
    print("\n--- Área do Gerente ---")
    while True:
        choice = _prompt_menu("Gerência", [
            ("1", "Cadastrar produto"),
            ("2", "Listar produtos"),
            ("3", "Estocar produto (criar item de estoque)"),
            ("4", "Repor estoque (restock)"),
            ("5", "Aplicar política de preço (desconto)"),
            ("6", "Relatório de estoque baixo"),
            ("0", "Voltar"),
        ])

        if choice == "1":
            try:
                store.product_ctrl.add()
            except (ValueError, KeyError) as e:
                print(f"Erro ao cadastrar produto: {e}")

        elif choice == "2":
            store.product_ctrl.list_all()

        elif choice == "3":
            product = store.product_ctrl.prompt_choice()
            if product is None:
                print("Nenhum produto cadastrado ainda.")
                continue
            try:
                aisle_number = int(input("Número do corredor: "))
                shelf_code = input("Código da prateleira: ").strip()
                qty = int(input("Quantidade inicial: "))
                min_stock_raw = input("Estoque mínimo [3]: ").strip()
                min_stock = int(min_stock_raw) if min_stock_raw else 3

                shelf = store.inventory_ctrl.find_shelf(shelf_code)
                if shelf is None:
                    shelf = store.inventory_ctrl.add_shelf(aisle_number, shelf_code)
                store.inventory_ctrl.stock_item(shelf, product, qty, min_stock)
            except ValueError as e:
                print(f"Erro: {e}")

        elif choice == "4":
            sku = input("SKU: ").strip()
            try:
                n = int(input("Quantidade a repor: "))
                store.inventory_ctrl.restock(sku, n)
            except ValueError as e:
                print(f"Erro: {e}")

        elif choice == "5":
            sku = input("SKU: ").strip()
            try:
                pct = float(input("Percentual de desconto (0-1, ex: 0.2 = 20%): "))
                store.product_ctrl.apply_policy(sku, Discount(pct))
            except ValueError as e:
                print(f"Erro: {e}")

        elif choice == "6":
            store.inventory_ctrl.low_stock_report()

        elif choice == "0":
            return
        else:
            print("Opção inválida.")


# ---------------------------------------------------------------------------
# fulfillment_flow -> listar orders, avançar status
# ---------------------------------------------------------------------------

def fulfillment_flow(store: Store) -> None:
    print("\n--- Área de Fulfillment ---")
    while True:
        choice = _prompt_menu("Fulfillment", [
            ("1", "Listar pedidos"),
            ("2", "Avançar status de um pedido"),
            ("0", "Voltar"),
        ])

        if choice == "1":
            store.checkout_ctrl.list_orders()

        elif choice == "2":
            order_id = input("ID do pedido: ").strip()
            try:
                store.checkout_ctrl.advance(order_id)
            except ValueError as e:
                print(f"Erro: {e}")

        elif choice == "0":
            return
        else:
            print("Opção inválida.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    store = Store()
    print("=" * 40)
    print("  STORE MVC")
    print("=" * 40)

    flows = {
        "1": customer_flow,
        "2": manager_flow,
        "3": fulfillment_flow,
    }

    while True:
        choice = _prompt_menu("Menu Principal", [
            ("1", "Área do Cliente"),
            ("2", "Área do Gerente"),
            ("3", "Área de Fulfillment"),
            ("0", "Sair"),
        ])

        if choice in flows:
            flows[choice](store)
        elif choice == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()