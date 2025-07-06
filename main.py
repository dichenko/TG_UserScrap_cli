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

async def export_chat_participants(chat_manager: ChatManager, chat_id: int, chat_title: str) -> bool:
    """Экспортирует участников чата"""
    # Получаем участников
    print("👥 Получение списка участников...")
    participants = await chat_manager.get_chat_participants(chat_id)
    
    if not participants:
        print("❌ Не удалось получить участников чата")
        return False
    
    # Запрашиваем подтверждение с реальным количеством участников
    if not UserInterface.confirm_export(chat_title, len(participants)):
        print("❌ Экспорт отменен")
        return False
    
    # Экспортируем в CSV
    print("📊 Экспорт в CSV...")
    filename = CSVExporter.export_participants(participants, chat_title)
    
    if filename:
        UserInterface.display_completion()
        print(f"📁 Файл сохранен: {filename}")
        return True
    else:
        print("❌ Ошибка при экспорте")
        return False

async def export_chat_messages(chat_manager: ChatManager, chat_id: int, chat_title: str) -> bool:
    """Экспортирует авторов сообщений из чата"""
    # Спрашиваем о количестве сообщений
    message_count = UserInterface.ask_for_message_count()
    
    # Анализируем сообщения
    users = await chat_manager.analyze_messages_for_users(chat_id, message_count)
    
    if not users:
        print("❌ Не удалось найти авторов сообщений")
        return False
    
    # Запрашиваем подтверждение
    if not UserInterface.confirm_export(chat_title, len(users)):
        print("❌ Экспорт отменен")
        return False
    
    # Экспортируем в CSV
    print("📊 Экспорт в CSV...")
    filename = CSVExporter.export_participants(users, chat_title)
    
    if filename:
        UserInterface.display_completion()
        print(f"📁 Файл сохранен: {filename}")
        return True
    else:
        print("❌ Ошибка при экспорте")
        return False

async def process_chat_selection(chat_manager: ChatManager, available_chats: list, unavailable_chats: list) -> bool:
    """Обрабатывает выбор чата и экспорт"""
    # Объединяем все чаты для выбора
    all_chats = available_chats + unavailable_chats
    
    if not all_chats:
        print("❌ Нет доступных чатов")
        return False
    
    # Выбираем чат
    selected_chat_id = UserInterface.select_chat(all_chats)
    if not selected_chat_id:
        print("❌ Чат не выбран")
        return False
    
    # Получаем информацию о выбранном чате
    selected_chat = await chat_manager.get_chat_by_id(selected_chat_id)
    if not selected_chat:
        print("❌ Не удалось получить информацию о чате")
        return False
    
    # Проверяем, доступен ли чат для получения участников
    is_available = any(chat['id'] == selected_chat_id for chat in available_chats)
    
    if is_available:
        # Экспортируем участников
        return await export_chat_participants(chat_manager, selected_chat_id, selected_chat['title'])
    else:
        # Спрашиваем об анализе сообщений
        if UserInterface.ask_for_message_analysis():
            return await export_chat_messages(chat_manager, selected_chat_id, selected_chat['title'])
        else:
            print("❌ Экспорт отменен")
            return False

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
        
        # Основной цикл программы
        while True:
            # Получаем список чатов с разделением по доступности
            print("📋 Получение списка чатов...")
            available_chats, unavailable_chats = await chat_manager.get_all_chats_with_access_status()
            
            # Отображаем чаты
            UserInterface.display_chats_with_access_status(available_chats, unavailable_chats)
            
            # Обрабатываем выбор чата и экспорт
            success = await process_chat_selection(chat_manager, available_chats, unavailable_chats)
            
            # Спрашиваем о продолжении
            if not UserInterface.ask_for_another_export():
                break
        
        # Отключаемся
        await auth.disconnect()
        print("👋 Программа завершена")
        
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