"""
Модуль для экспорта данных в CSV файл
"""
import csv
import os
import re
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CSVExporter:
    """Класс для экспорта данных в CSV"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очищает название файла от недопустимых символов"""
        # Удаляем символы, недопустимые в именах файлов Windows
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Удаляем лишние пробелы и подчеркивания
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        sanitized = re.sub(r'_+', '_', sanitized)
        
        return sanitized
    
    @staticmethod
    def export_participants(participants: List[Dict], chat_title: str) -> str:
        """Экспортирует участников в CSV файл с расширенной информацией"""
        if not participants:
            print("❌ Нет участников для экспорта")
            return ""
        
        # Формируем имя файла
        current_date = datetime.now().strftime("%Y-%m-%d")
        sanitized_title = CSVExporter.sanitize_filename(chat_title)
        filename = f"{sanitized_title} - {current_date}.csv"
        
        # Путь к папке output
        output_dir = "output"
        output_path = os.path.join(output_dir, filename)
        
        try:
            # Создаем папку output, если её нет
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Определяем заголовки на основе доступных полей
                fieldnames = [
                    'TGid', 'Username', 'Usersurname', 'First_Name', 'Last_Name', 
                    'Phone', 'Bio', 'Premium', 'Verified', 'Bot', 'Deleted', 
                    'Scam', 'Fake', 'Status', 'Last_Seen'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Записываем данные
                for participant in participants:
                    row = {
                        'TGid': participant.get('tgid', ''),
                        'Username': f"@{participant.get('username', '')}" if participant.get('username') else '',
                        'Usersurname': participant.get('usersurname', ''),
                        'First_Name': participant.get('first_name', ''),
                        'Last_Name': participant.get('last_name', ''),
                        'Phone': participant.get('phone', ''),
                        'Bio': participant.get('bio', ''),
                        'Premium': 'Да' if participant.get('premium', False) else 'Нет',
                        'Verified': 'Да' if participant.get('verified', False) else 'Нет',
                        'Bot': 'Да' if participant.get('bot', False) else 'Нет',
                        'Deleted': 'Да' if participant.get('deleted', False) else 'Нет',
                        'Scam': 'Да' if participant.get('scam', False) else 'Нет',
                        'Fake': 'Да' if participant.get('fake', False) else 'Нет',
                        'Status': participant.get('status', ''),
                        'Last_Seen': participant.get('last_seen', '')
                    }
                    writer.writerow(row)
            
            print(f"✅ Данные успешно экспортированы в файл: {output_path}")
            print(f"📊 Экспортировано участников: {len(participants)}")
            print(f"📋 Поля: {', '.join(fieldnames)}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка при экспорте в CSV: {e}")
            print(f"❌ Ошибка при создании файла: {e}")
            return "" 