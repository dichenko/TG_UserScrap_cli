"""
Модуль для работы с чатами и получения списка участников
"""
import logging
import asyncio
import random
from typing import List, Dict, Optional, Tuple
from telethon import TelegramClient
from telethon.tl.types import (
    Channel, 
    Chat, 
    User,
    ChatFull,
    ChannelFull,
    Message,
    UserStatusOnline,
    UserStatusOffline,
    UserStatusRecently,
    UserStatusLastWeek,
    UserStatusLastMonth
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
    
    async def _get_detailed_user_info(self, user: User) -> Dict:
        """Получает детальную информацию о пользователе"""
        user_info = {
            'tgid': user.id,
            'username': user.username or '',
            'usersurname': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'phone': user.phone or '',
            'bio': '',
            'premium': False,
            'verified': False,
            'bot': False,
            'deleted': False,
            'scam': False,
            'fake': False,
            'location': '',
            'status': 'unknown',
            'last_seen': '',
            'common_chats_count': 0
        }
        
        try:
            # Получаем полную информацию о пользователе
            full_user = await self.client.get_entity(user.id)
            
            # Обновляем информацию
            if hasattr(full_user, 'about') and full_user.about:
                user_info['bio'] = full_user.about
            
            if hasattr(full_user, 'premium') and full_user.premium:
                user_info['premium'] = True
                
            if hasattr(full_user, 'verified') and full_user.verified:
                user_info['verified'] = True
                
            if hasattr(full_user, 'bot') and full_user.bot:
                user_info['bot'] = True
                
            if hasattr(full_user, 'deleted') and full_user.deleted:
                user_info['deleted'] = True
                
            if hasattr(full_user, 'scam') and full_user.scam:
                user_info['scam'] = True
                
            if hasattr(full_user, 'fake') and full_user.fake:
                user_info['fake'] = True
                
            # Определяем статус пользователя
            if hasattr(full_user, 'status'):
                if isinstance(full_user.status, UserStatusOnline):
                    user_info['status'] = 'online'
                elif isinstance(full_user.status, UserStatusOffline):
                    user_info['status'] = 'offline'
                    if hasattr(full_user.status, 'was_online'):
                        user_info['last_seen'] = str(full_user.status.was_online)
                elif isinstance(full_user.status, UserStatusRecently):
                    user_info['status'] = 'recently'
                elif isinstance(full_user.status, UserStatusLastWeek):
                    user_info['status'] = 'last_week'
                elif isinstance(full_user.status, UserStatusLastMonth):
                    user_info['status'] = 'last_month'
                    
        except Exception as e:
            logger.warning(f"Не удалось получить детальную информацию о пользователе {user.id}: {e}")
        
        return user_info
    
    async def _add_delay(self):
        """Добавляет случайную задержку 1-3 секунды"""
        delay = random.uniform(0.3, 1.0)
        await asyncio.sleep(delay)
    
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
    
    async def get_all_chats_with_access_status(self) -> Tuple[List[Dict], List[Dict]]:
        """Получает все чаты, разделенные на доступные и недоступные"""
        available_chats = []
        unavailable_chats = []
        
        try:
            # Получаем все диалоги
            async for dialog in self.client.iter_dialogs():
                chat = dialog.entity
                
                # Проверяем, что это группа, супергруппа или канал
                if isinstance(chat, (Channel, Chat)):
                    chat_info = {
                        'id': chat.id,
                        'title': chat.title,
                        'type': 'Канал' if isinstance(chat, Channel) and chat.broadcast else 'Группа'
                    }
                    
                    try:
                        # Получаем полную информацию о чате
                        full_chat = await self.client.get_entity(chat.id)
                        
                        # Проверяем, есть ли доступ к участникам
                        if hasattr(full_chat, 'participants_count') and full_chat.participants_count:
                            chat_info['participants_count'] = full_chat.participants_count
                            available_chats.append(chat_info)
                        else:
                            unavailable_chats.append(chat_info)
                            
                    except (ChatAdminRequiredError, ChannelPrivateError):
                        # Чаты без доступа к участникам
                        unavailable_chats.append(chat_info)
                    except Exception as e:
                        logger.warning(f"Ошибка при получении информации о чате {chat.title}: {e}")
                        unavailable_chats.append(chat_info)
                        
        except FloodWaitError as e:
            print(f"❌ Слишком много запросов. Подождите {e.seconds} секунд")
            return [], []
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка чатов: {e}")
            return [], []
        
        return available_chats, unavailable_chats
    
    async def get_chat_participants(self, chat_id: int) -> List[Dict]:
        """Получает список участников чата с расширенной информацией"""
        participants = []
        
        try:
            print("👥 Получение списка участников...")
            
            # Получаем участников чата
            async for participant in self.client.iter_participants(chat_id):
                if isinstance(participant, User):
                    # Получаем детальную информацию о пользователе
                    participant_info = await self._get_detailed_user_info(participant)
                    participants.append(participant_info)
                    
                    # Добавляем задержку между запросами
                    await self._add_delay()
                    
                    # Показываем прогресс каждые 25 пользователей
                    if len(participants) % 25 == 0:
                        print(f"📊 Обработано участников: {len(participants)}")
                    
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
        
        print(f"✅ Получено участников: {len(participants)}")
        return participants
    
    async def get_total_message_count(self, chat_id: int) -> int:
        """Получает общее количество сообщений в чате"""
        try:
            # Получаем общее количество сообщений
            total_messages = await self.client.get_messages(chat_id, limit=0)
            return total_messages
        except Exception as e:
            logger.error(f"❌ Ошибка при получении количества сообщений: {e}")
            return 0
    
    async def analyze_messages_for_users(self, chat_id: int, limit: int) -> List[Dict]:
        """Анализирует сообщения для извлечения авторов с расширенной информацией"""
        users = {}
        
        try:
            if limit == -1:  # Все сообщения
                total_messages = await self.get_total_message_count(chat_id)
                print(f"📊 Анализ всех сообщений ({total_messages} сообщений)...")
                message_iterator = self.client.iter_messages(chat_id)
            else:
                print(f"📊 Анализ {limit} последних сообщений...")
                message_iterator = self.client.iter_messages(chat_id, limit=limit)
            
            processed_count = 0
            
            async for message in message_iterator:
                if message and message.sender and isinstance(message.sender, User):
                    user_id = message.sender.id
                    
                    # Добавляем пользователя только если его еще нет
                    if user_id not in users:
                        user_info = await self._get_detailed_user_info(message.sender)
                        users[user_id] = user_info
                        
                        # Добавляем задержку между запросами
                        await self._add_delay()
                
                processed_count += 1
                
                # Показываем прогресс каждые 250 сообщений
                if processed_count % 250 == 0:
                    print(f"📊 Обработано сообщений: {processed_count}, найдено авторов: {len(users)}")
                
                # Если достигли лимита (кроме случая "все сообщения")
                if limit != -1 and processed_count >= limit:
                    break
                        
        except FloodWaitError as e:
            print(f"⏳ Слишком много запросов. Ждем {e.seconds} секунд...")
            await asyncio.sleep(e.seconds)
            # Пытаемся продолжить анализ
            return await self.analyze_messages_for_users(chat_id, limit)
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе сообщений: {e}")
            print(f"❌ Ошибка при анализе сообщений: {e}")
            return []
        
        # Преобразуем словарь в список
        users_list = list(users.values())
        print(f"✅ Найдено уникальных авторов: {len(users_list)}")
        return users_list
    
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