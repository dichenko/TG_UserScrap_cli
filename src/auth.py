"""
Модуль авторизации в Telegram
"""
import logging
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError, 
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError
)
from .config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramAuth:
    """Класс для авторизации в Telegram"""
    
    def __init__(self):
        self.client = None
        
    async def connect(self) -> bool:
        """Подключение к Telegram API"""
        try:
            self.client = TelegramClient(
                Config.SESSION_NAME,
                int(Config.TELEGRAM_API_ID),
                Config.TELEGRAM_API_HASH
            )
            
            await self.client.connect()
            logger.info("✅ Подключение к Telegram API установлено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Telegram API: {e}")
            return False
    
    async def authenticate(self) -> bool:
        """Авторизация пользователя"""
        if not self.client:
            logger.error("❌ Клиент не инициализирован")
            return False
        
        try:
            # Проверяем, авторизован ли уже пользователь
            if await self.client.is_user_authorized():
                logger.info("✅ Пользователь уже авторизован")
                return True
            
            # Запрашиваем номер телефона
            phone = input("📱 Введите номер телефона (с кодом страны, например +7): ")
            
            # Отправляем код подтверждения
            await self.client.send_code_request(phone)
            
            # Запрашиваем код
            code = input("🔐 Введите код подтверждения из Telegram: ")
            
            try:
                await self.client.sign_in(phone, code)
                logger.info("✅ Авторизация успешна")
                return True
                
            except PhoneCodeInvalidError:
                print("❌ Неверный код подтверждения")
                return False
                
            except SessionPasswordNeededError:
                # Если включена двухфакторная аутентификация
                password = input("🔒 Введите пароль двухфакторной аутентификации: ")
                try:
                    await self.client.sign_in(password=password)
                    logger.info("✅ Авторизация с 2FA успешна")
                    return True
                except Exception as e:
                    print(f"❌ Ошибка при вводе пароля 2FA: {e}")
                    return False
                    
        except PhoneNumberInvalidError:
            print("❌ Неверный номер телефона")
            return False
            
        except FloodWaitError as e:
            print(f"❌ Слишком много запросов. Подождите {e.seconds} секунд")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от Telegram API"""
        if self.client:
            await self.client.disconnect()
            logger.info("🔌 Отключение от Telegram API")
    
    def get_client(self) -> TelegramClient:
        """Возвращает клиент для использования в других модулях"""
        return self.client 