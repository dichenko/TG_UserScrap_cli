"""
Модуль пользовательского интерфейса
"""
from typing import List, Dict, Optional

class UserInterface:
    """Класс для взаимодействия с пользователем"""
    
    @staticmethod
    def display_welcome():
        """Отображает приветственное сообщение"""
        print("=" * 60)
        print("📱 Telegram Chat Exporter")
        print("=" * 60)
        print("Программа для экспорта участников из Telegram-чатов")
        print()
    
    @staticmethod
    def display_chats(chats: List[Dict]):
        """Отображает список доступных чатов"""
        if not chats:
            print("❌ Не найдено доступных чатов с участниками")
            return
        
        print(f"📋 Найдено доступных чатов: {len(chats)}")
        print("-" * 60)
        
        for i, chat in enumerate(chats, 1):
            print(f"{i:2d}. {chat['title']}")
            print(f"    ID: {chat['id']} | Тип: {chat['type']} | Участников: {chat['participants_count']}")
            print()
    
    @staticmethod
    def display_chats_with_access_status(available_chats: List[Dict], unavailable_chats: List[Dict]):
        """Отображает чаты, разделенные на доступные и недоступные"""
        print("📋 Список чатов:")
        print("=" * 60)
        
        # Доступные чаты
        if available_chats:
            print(f"✅ Доступные чаты ({len(available_chats)}):")
            print("-" * 40)
            for i, chat in enumerate(available_chats, 1):
                print(f"{i:2d}. {chat['title']}")
                print(f"    ID: {chat['id']} | Тип: {chat['type']} | Участников: {chat['participants_count']}")
                print()
        else:
            print("❌ Нет доступных чатов с участниками")
            print()
        
        # Недоступные чаты
        if unavailable_chats:
            print(f"❌ Недоступные чаты ({len(unavailable_chats)}):")
            print("-" * 40)
            for i, chat in enumerate(unavailable_chats, len(available_chats) + 1):
                print(f"{i:2d}. {chat['title']}")
                print(f"    ID: {chat['id']} | Тип: {chat['type']}")
                print()
        else:
            print("❌ Нет недоступных чатов")
            print()
    
    @staticmethod
    def select_chat(all_chats: List[Dict]) -> Optional[int]:
        """Позволяет пользователю выбрать чат"""
        if not all_chats:
            return None
        
        while True:
            try:
                choice = input("🔍 Выберите номер чата или введите ID чата: ").strip()
                
                # Если введен номер из списка
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(all_chats):
                        selected_chat = all_chats[choice_num - 1]
                        print(f"✅ Выбран чат: {selected_chat['title']}")
                        return selected_chat['id']
                    else:
                        print(f"❌ Номер должен быть от 1 до {len(all_chats)}")
                        continue
                
                # Если введен ID чата
                try:
                    chat_id = int(choice)
                    # Проверяем, есть ли такой чат в списке
                    for chat in all_chats:
                        if chat['id'] == chat_id:
                            print(f"✅ Выбран чат: {chat['title']}")
                            return chat_id
                    
                    print("❌ Чат с таким ID не найден в списке")
                    continue
                    
                except ValueError:
                    print("❌ Введите корректный номер или ID чата")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Операция отменена пользователем")
                return None
    
    @staticmethod
    def confirm_export(chat_title: str, participants_count: int) -> bool:
        """Запрашивает подтверждение экспорта"""
        print(f"📊 Подготовка к экспорту:")
        print(f"   Чат: {chat_title}")
        print(f"   Участников: {participants_count}")
        print()
        
        while True:
            confirm = input("🚀 Начать экспорт? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', 'да', 'д']:
                return True
            elif confirm in ['n', 'no', 'нет', 'н']:
                return False
            else:
                print("❌ Введите 'y' или 'n'")
    
    @staticmethod
    def ask_for_message_analysis() -> bool:
        """Спрашивает, хочет ли пользователь проанализировать сообщения"""
        print("❌ У вас нет доступа к списку участников этого чата.")
        print()
        
        while True:
            confirm = input("Хотите проанализировать последние сообщения, чтобы попытаться извлечь авторов? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', 'да', 'д']:
                return True
            elif confirm in ['n', 'no', 'нет', 'н']:
                return False
            else:
                print("❌ Введите 'y' или 'n'")
    
    @staticmethod
    def ask_for_message_count() -> int:
        """Спрашивает количество сообщений для анализа"""
        while True:
            try:
                count = input("Введите количество сообщений для анализа: ").strip()
                count_num = int(count)
                if count_num > 0:
                    return count_num
                else:
                    print("❌ Количество должно быть больше 0")
            except ValueError:
                print("❌ Введите корректное число")
    
    @staticmethod
    def ask_for_another_export() -> bool:
        """Спрашивает, хочет ли пользователь выгрузить пользователей из другого чата"""
        print()
        while True:
            confirm = input("Хотите выгрузить пользователей из другого чата? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', 'да', 'д']:
                return True
            elif confirm in ['n', 'no', 'нет', 'н']:
                return False
            else:
                print("❌ Введите 'y' или 'n'")
    
    @staticmethod
    def display_progress(current: int, total: int):
        """Отображает прогресс обработки"""
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"\r📊 Обработано: {current}/{total} ({percentage:.1f}%)", end="", flush=True)
    
    @staticmethod
    def display_completion():
        """Отображает сообщение о завершении"""
        print("\n✅ Экспорт завершен!")
        print("=" * 60) 