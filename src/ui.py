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
    def select_chat(chats: List[Dict]) -> Optional[int]:
        """Позволяет пользователю выбрать чат"""
        if not chats:
            return None
        
        while True:
            try:
                choice = input("🔍 Выберите номер чата или введите ID чата: ").strip()
                
                # Если введен номер из списка
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(chats):
                        selected_chat = chats[choice_num - 1]
                        print(f"✅ Выбран чат: {selected_chat['title']}")
                        return selected_chat['id']
                    else:
                        print(f"❌ Номер должен быть от 1 до {len(chats)}")
                        continue
                
                # Если введен ID чата
                try:
                    chat_id = int(choice)
                    # Проверяем, есть ли такой чат в списке
                    for chat in chats:
                        if chat['id'] == chat_id:
                            print(f"✅ Выбран чат: {chat['title']}")
                            return chat_id
                    
                    print("❌ Чат с таким ID не найден в списке доступных")
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
    def display_progress(current: int, total: int):
        """Отображает прогресс обработки"""
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"\r📊 Обработано: {current}/{total} ({percentage:.1f}%)", end="", flush=True)
    
    @staticmethod
    def display_completion():
        """Отображает сообщение о завершении"""
        print("\n✅ Экспорт завершен!")
        print("=" * 60) 