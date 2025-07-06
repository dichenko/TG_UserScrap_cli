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
        """Экспортирует участников в CSV файл"""
        if not participants:
            print("❌ Нет участников для экспорта")
            return ""
        
        # Формируем имя файла
        current_date = datetime.now().strftime("%Y-%m-%d")
        sanitized_title = CSVExporter.sanitize_filename(chat_title)
        filename = f"{sanitized_title} - {current_date}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Записываем заголовки
                fieldnames = ['TGid', 'Username', 'Usersurname']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Записываем данные
                for participant in participants:
                    writer.writerow({
                        'TGid': participant['tgid'],
                        'Username': f"@{participant['username']}" if participant['username'] else '',
                        'Usersurname': participant['usersurname']
                    })
            
            print(f"✅ Данные успешно экспортированы в файл: {filename}")
            print(f"📊 Экспортировано участников: {len(participants)}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Ошибка при экспорте в CSV: {e}")
            print(f"❌ Ошибка при создании файла: {e}")
            return "" 