"""
Модуль конфигурации для загрузки переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    """Класс конфигурации приложения"""
    
    # Telegram API credentials
    TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
    SESSION_NAME = os.getenv('SESSION_NAME', 'anon')
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность конфигурации"""
        if not cls.TELEGRAM_API_ID:
            print("❌ Ошибка: TELEGRAM_API_ID не найден в .env файле")
            return False
        
        if not cls.TELEGRAM_API_HASH:
            print("❌ Ошибка: TELEGRAM_API_HASH не найден в .env файле")
            return False
        
        try:
            int(cls.TELEGRAM_API_ID)
        except ValueError:
            print("❌ Ошибка: TELEGRAM_API_ID должен быть числом")
            return False
        
        return True 