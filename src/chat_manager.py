"""
Модуль для работы с чатами и получения списка участников
"""
import logging
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.types import (
    Channel, 
    Chat, 
    User,
    ChatFull,
    ChannelFull
)
from telethon.errors import (
    FloodWaitError,
    ChatAdminRequiredError,
    ChannelPrivateError
)

logger = logging.getLogger(__name__)

class ChatManager:
    """Класс для работы с чатами"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
    
    async def get_available_chats(self) -> List[Dict]:
        """Получает список доступных чатов с участниками"""
        available_chats = []
        
        try:
            # Получаем все диалоги
            async for dialog in self.client.iter_dialogs():
                chat = dialog.entity
                
                # Проверяем, что это группа, супергруппа или канал
                if isinstance(chat, (Channel, Chat)):
                    try:
                        # Получаем полную информацию о чате
                        full_chat = await self.client.get_entity(chat.id)
                        
                        # Проверяем, есть ли доступ к участникам
                        if hasattr(full_chat, 'participants_count') and full_chat.participants_count:
                            chat_info = {
                                'id': chat.id,
                                'title': chat.title,
                                'participants_count': full_chat.participants_count,
                                'type': 'Канал' if isinstance(chat, Channel) and chat.broadcast else 'Группа'
                            }
                            available_chats.append(chat_info)
                            
                    except (ChatAdminRequiredError, ChannelPrivateError):
                        # Пропускаем чаты без доступа к участникам
                        continue
                    except Exception as e:
                        logger.warning(f"Ошибка при получении информации о чате {chat.title}: {e}")
                        continue
                        
        except FloodWaitError as e:
            print(f"❌ Слишком много запросов. Подождите {e.seconds} секунд")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка чатов: {e}")
            return []
        
        return available_chats
    
    async def get_chat_participants(self, chat_id: int) -> List[Dict]:
        """Получает список участников чата"""
        participants = []
        
        try:
            # Получаем участников чата
            async for participant in self.client.iter_participants(chat_id):
                if isinstance(participant, User):
                    # Получаем актуальную информацию о пользователе
                    try:
                        user = await self.client.get_entity(participant.id)
                        if isinstance(user, User):
                            participant_info = {
                                'tgid': user.id,
                                'username': user.username or '',
                                'usersurname': f"{user.first_name or ''} {user.last_name or ''}".strip()
                            }
                            participants.append(participant_info)
                    except Exception as e:
                        # Если не удалось получить актуальную информацию, используем данные из чата
                        logger.warning(f"Не удалось получить актуальную информацию о пользователе {participant.id}: {e}")
                        participant_info = {
                            'tgid': participant.id,
                            'username': participant.username or '',
                            'usersurname': f"{participant.first_name or ''} {participant.last_name or ''}".strip()
                        }
                        participants.append(participant_info)
                    
        except ChatAdminRequiredError:
            print("❌ Ошибка: Нет доступа к списку участников. Требуются права администратора.")
            return []
        except ChannelPrivateError:
            print("❌ Ошибка: Приватный канал. Нет доступа к участникам.")
            return []
        except FloodWaitError as e:
            print(f"❌ Слишком много запросов. Подождите {e.seconds} секунд")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка при получении участников: {e}")
            return []
        
        return participants
    
    async def get_chat_by_id(self, chat_id: int) -> Optional[Dict]:
        """Получает информацию о чате по ID"""
        try:
            chat = await self.client.get_entity(chat_id)
            if isinstance(chat, (Channel, Chat)):
                return {
                    'id': chat.id,
                    'title': chat.title,
                    'type': 'Канал' if isinstance(chat, Channel) and chat.broadcast else 'Группа'
                }
        except Exception as e:
            logger.error(f"❌ Ошибка при получении чата по ID {chat_id}: {e}")
            return None
        
        return None 