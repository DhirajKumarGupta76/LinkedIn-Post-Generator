from cryptography.fernet import Fernet

from app.config import get_config


class EncryptionService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            key = get_config().get('ENCRYPTION_KEY')
            if not key:
                raise ValueError('ENCRYPTION_KEY must be configured for reversible encryption.')
            cls._instance.fernet = Fernet(key.encode())
        return cls._instance

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()


# Passwords should never be encrypted because encryption is reversible.
# Hashing is the correct choice for passwords because it is one-way and designed
# to slow brute-force attacks. We only use Fernet for truly sensitive data that
# must be reversible, such as tokens or fields that need to be read back later.
