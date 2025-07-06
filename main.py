#!/usr/bin/env python3
"""
Главный файл программы Telegram Chat Exporter
"""
import asyncio
import sys
import logging
from src.config import Config
from src.auth import TelegramAuth
from src.chat_manager import ChatManager
from src.csv_exporter import CSVExporter
from src.ui import UserInterface

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция программы"""
    try:
        # Отображаем приветствие
        UserInterface.display_welcome()
        
        # Проверяем конфигурацию
        if not Config.validate():
            print("\n📝 Создайте файл .env на основе env.example и заполните свои данные")
            return
        
        # Инициализируем авторизацию
        auth = TelegramAuth()
        
        # Подключаемся к Telegram
        print("🔌 Подключение к Telegram API...")
        if not await auth.connect():
            print("❌ Не удалось подключиться к Telegram API")
            return
        
        # Авторизуемся
        print("🔐 Авторизация...")
        if not await auth.authenticate():
            print("❌ Не удалось авторизоваться")
            await auth.disconnect()
            return
        
        # Получаем клиент
        client = auth.get_client()
        chat_manager = ChatManager(client)
        
        # Получаем список доступных чатов
        print("📋 Получение списка чатов...")
        chats = await chat_manager.get_available_chats()
        
        # Отображаем чаты
        UserInterface.display_chats(chats)
        
        # Выбираем чат
        selected_chat_id = UserInterface.select_chat(chats)
        if not selected_chat_id:
            print("❌ Чат не выбран")
            await auth.disconnect()
            return
        
        # Получаем информацию о выбранном чате
        selected_chat = await chat_manager.get_chat_by_id(selected_chat_id)
        if not selected_chat:
            print("❌ Не удалось получить информацию о чате")
            await auth.disconnect()
            return
        
        # Запрашиваем подтверждение экспорта
        if not UserInterface.confirm_export(selected_chat['title'], 0):
            print("❌ Экспорт отменен")
            await auth.disconnect()
            return
        
        # Получаем участников
        print("👥 Получение списка участников...")
        participants = await chat_manager.get_chat_participants(selected_chat_id)
        
        if not participants:
            print("❌ Не удалось получить участников чата")
            await auth.disconnect()
            return
        
        # Запрашиваем подтверждение с реальным количеством участников
        if not UserInterface.confirm_export(selected_chat['title'], len(participants)):
            print("❌ Экспорт отменен")
            await auth.disconnect()
            return
        
        # Экспортируем в CSV
        print("📊 Экспорт в CSV...")
        filename = CSVExporter.export_participants(participants, selected_chat['title'])
        
        if filename:
            UserInterface.display_completion()
            print(f"📁 Файл сохранен: {filename}")
        else:
            print("❌ Ошибка при экспорте")
        
        # Отключаемся
        await auth.disconnect()
        
    except KeyboardInterrupt:
        print("\n❌ Программа прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    # Проверяем версию Python
    if sys.version_info < (3, 7):
        print("❌ Требуется Python 3.7 или выше")
        sys.exit(1)
    
    # Запускаем программу
    asyncio.run(main()) 