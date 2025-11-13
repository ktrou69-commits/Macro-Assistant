#!/usr/bin/env python3
"""
Пример использования модуля VideoProcessor
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.video_processor.main import VideoProcessor

def main():
    # Создание модуля
    module = VideoProcessor()
    
    # Тестовые запросы
    test_requests = [
        "Привет, что ты умеешь?",
        "Помоги мне с задачей",
        "Покажи свои возможности"
    ]
    
    print(f"🧪 Тестирование модуля VideoProcessor")
    print("=" * 50)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        result = module.handle(request)
        
        if result.get("success"):
            print(f"   ✅ Результат: {result.get('result', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'N/A')}")

if __name__ == "__main__":
    main()
