from typing import Protocol


class PasswordHasher(Protocol):
    def hashear(self, password: str) -> str: ...

    def verificar(self, password: str, password_hash: str) -> bool: ...
