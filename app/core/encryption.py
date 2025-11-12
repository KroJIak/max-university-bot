import os
from cryptography.fernet import Fernet
from typing import Optional


class EncryptionService:
    """Сервис для шифрования/дешифрования паролей"""
    
    def __init__(self):
        # Получаем ключ из переменной окружения
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        
        # Fernet принимает ключ как bytes, но если это строка, используем её напрямую
        # Fernet автоматически обработает строку
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}")
    
    def encrypt(self, password: str) -> str:
        """Зашифровать пароль"""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt(self, encrypted_password: str) -> str:
        """Расшифровать пароль"""
        return self.cipher.decrypt(encrypted_password.encode()).decode()


# Глобальный экземпляр (будет инициализирован при первом использовании)
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Получить экземпляр сервиса шифрования"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service

