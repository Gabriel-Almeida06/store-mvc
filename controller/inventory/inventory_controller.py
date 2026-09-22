from model.inventory import *
from model.product import Product
from view.inventory.inventory_view import InventoryView

class InventoryController:
    def __init__(self, view: InventoryView):
        self._aisles: list[Aisle] = []
        self._view = view

    @property
    def aisles(self):
        return list(self._aisles)

    def add_aisle(self, number: int) -> Aisle:
        aisle = Aisle(number)
        self._aisles.append(aisle)
        return aisle

    def find_aisle(self, number: int) -> Aisle | None:
        for aisle in self._aisles:
            if aisle.number == number:
                return aisle
        return None

    def add_shelf(self, aisle_number: int, code: str) -> Shelf:
        aisle = self.find_aisle(aisle_number)
        if aisle is None:
            aisle = self.add_aisle(aisle_number)
        shelf = Shelf(code)
        aisle.add_shelf(shelf)
        return shelf

    def find_shelf(self, code: str) -> Shelf | None:
        for aisle in self._aisles:
            for shelf in aisle.shelves:
                if shelf.code == code:
                    return shelf
        return None

    def stock_item(self, shelf: Shelf, product: Product, qty: int, min_stock: int = 3) -> None:
        item = StockItem(product, qty, min_stock)
        shelf.add_item(item)
        self._view.show(item)

    def restock(self, sku: str, n: int) -> None:
        item = self._find(sku)
        if item:
            item.add(n)
            self._view.show(item)
        else:
            raise ValueError(f"SKU {sku} não encontrado no estoque")

    def low_stock_report(self) -> None:
        found = False
        for aisle in self._aisles:
            for shelf in aisle.shelves:
                for item in shelf.items:
                    if item.low_stock():
                        self._view.show_alert(item)
                        found = True
        if not found:
            self._view.show_list([])

    def _find(self, sku: str) -> StockItem | None:
        for aisle in self._aisles:
            item = aisle.find(sku)
            if item:
                return item
        return None