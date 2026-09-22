from model.inventory import StockItem

class InventoryView:
    def show(self, item: StockItem) -> None:
        print(item)

    def show_list(self, items: list[StockItem]) -> None:
        for item in items:
            print(item)

    def show_alert(self, item: StockItem) -> None:
        print(f"Warning! Low Stock on {item}")

    def prompt_data(self) -> dict:
        return {
            "sku": input("SKU: "),
            "quantity": int(input("Quantity: ")),
            "min_stock": int(input("Min stock: ")),
            "shelf": input("Shelf code: "),
        }