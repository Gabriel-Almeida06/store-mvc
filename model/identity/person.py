from dataclasses import dataclass
from abc import ABC

# Value Objects
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str

    def __post_init__(self):
        if not self.street or not self.city or not self.zip_code:
            raise ValueError("street, city e zip_code não podem ser vazios")

    def __str__(self):
        return f"{self.street}, {self.city} - {self.zip_code}"

@dataclass(frozen=True)
class Contact:
    email: str
    phone: str

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("email inválido")
        if not self.phone:
            raise ValueError("phone não pode ser vazio")

    def __str__(self):
        return f"{self.email} / {self.phone}"

# ABCDEFG... python é estranho mesmo
class Person(ABC):
    def __init__(self, name: str, address: Address, contact: Contact):
        if not name or not name.strip():
            raise ValueError("name não pode ser vazio")
        self._name = name
        self._address = address
        self._contact = contact

    @property
    def name(self):
        return self._name
    @property
    def address(self):
        return self._address
    @property
    def contact(self):
        return self._contact