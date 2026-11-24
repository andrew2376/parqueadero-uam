from argon2 import PasswordHasher, profiles
from argon2.exceptions import InvalidHashError, VerificationError


class PasswordHasherArgon2:
    def __init__(self) -> None:
        self._hasher = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)

    def hashear(self, password: str) -> str:
        return self._hasher.hash(password)

    def verificar(self, password: str, password_hash: str) -> bool:
        if not password_hash.startswith("$argon2id$"):
            return False

        try:
            return self._hasher.verify(password_hash, password)
        except (InvalidHashError, VerificationError):
            return False
