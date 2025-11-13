#!/usr/bin/env python3
"""
🧩 Шаблон Модуля для Macro-Assistant
Используй этот файл как основу для создания новых модулей
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModuleTemplate:
    """
    Базовый шаблон для создания AI модулей
    
    Каждый модуль должен:
    1. Наследоваться от BaseModule
    2. Иметь метод handle(user_input, context)
    3. Возвращать стандартизированный результат
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Инициализация модуля
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.module_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.prompt_template = self._load_prompt()
        
        logger.info(f"✅ Модуль {self.config['name']} инициализирован")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации модуля"""
        config_file = self.module_dir / config_path
        
        if not config_file.exists():
            logger.warning(f"⚠️ Конфиг не найден: {config_file}")
            return self._default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "name": "module_template",
            "description": "Шаблон для создания новых модулей",
            "version": "1.0.0",
            "ai_model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 30
        }
    
    def _load_prompt(self) -> str:
        """Загрузка базового промпта"""
        prompt_file = self.module_dir / "prompts" / "base_prompt.txt"
        
        if not prompt_file.exists():
            logger.warning(f"⚠️ Промпт не найден: {prompt_file}")
            return self._default_prompt()
        
        try:
            return prompt_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки промпта: {e}")
            return self._default_prompt()
    
    def _default_prompt(self) -> str:
        """Промпт по умолчанию"""
        return """
Ты эксперт по автоматизации задач в системе Macro-Assistant.

ТВОЯ ЗАДАЧА:
Анализировать запросы пользователя и предоставлять полезные результаты.

ФОРМАТ ОТВЕТА:
Отвечай в формате JSON:
{
    "success": true/false,
    "result": "твой результат",
    "explanation": "объяснение что ты сделал",
    "suggestions": ["предложение 1", "предложение 2"]
}

ПОЛЬЗОВАТЕЛЬ: {user_input}
"""
    
    def handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Основной метод обработки запроса
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения (переменные, история и т.д.)
            
        Returns:
            Стандартизированный результат
        """
        try:
            logger.info(f"🔄 Обработка запроса: {user_input[:50]}...")
            
            # Подготовка контекста
            if context is None:
                context = {}
            
            # Формирование промпта
            full_prompt = self._build_prompt(user_input, context)
            
            # Вызов AI (здесь заглушка)
            ai_result = self._call_ai(full_prompt)
            
            # Обработка результата
            result = self._process_result(ai_result, user_input, context)
            
            logger.info(f"✅ Запрос обработан успешно")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки запроса: {e}")
            return {
                "success": False,
                "error": str(e),
                "module": self.config["name"],
                "user_input": user_input
            }
    
    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Построение полного промпта для AI
        
        Args:
            user_input: Ввод пользователя
            context: Контекст
            
        Returns:
            Готовый промпт
        """
        # Подставляем переменные в шаблон
        prompt = self.prompt_template.format(
            user_input=user_input,
            context=context,
            module_name=self.config["name"]
        )
        
        return prompt
    
    def _call_ai(self, prompt: str) -> str:
        """
        Вызов AI модели
        
        Args:
            prompt: Промпт для AI
            
        Returns:
            Ответ AI
        """
        # TODO: Здесь должен быть реальный вызов AI
        # Например, через OpenAI API или локальную модель
        
        # Заглушка для демонстрации
        mock_response = {
            "success": True,
            "result": f"Обработан запрос в модуле {self.config['name']}",
            "explanation": "Это демонстрационный ответ от шаблона модуля",
            "suggestions": [
                "Попробуйте более конкретный запрос",
                "Используйте ключевые слова для лучшего понимания"
            ]
        }
        
        return json.dumps(mock_response, ensure_ascii=False, indent=2)
    
    def _process_result(self, ai_result: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка результата от AI
        
        Args:
            ai_result: Ответ от AI
            user_input: Исходный запрос
            context: Контекст
            
        Returns:
            Обработанный результат
        """
        try:
            # Парсим JSON ответ от AI
            parsed_result = json.loads(ai_result)
            
            # Добавляем метаданные
            parsed_result.update({
                "module": self.config["name"],
                "timestamp": self._get_timestamp(),
                "user_input": user_input
            })
            
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON от AI: {e}")
            return {
                "success": False,
                "error": "Некорректный ответ от AI",
                "raw_response": ai_result,
                "module": self.config["name"]
            }
    
    def _get_timestamp(self) -> str:
        """Получение текущего времени"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_info(self) -> Dict[str, Any]:
        """Информация о модуле"""
        return {
            "name": self.config["name"],
            "description": self.config["description"],
            "version": self.config["version"],
            "status": "ready"
        }

# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создание и тестирование модуля
    module = ModuleTemplate()
    
    # Тестовые запросы
    test_requests = [
        "Создай простой макрос",
        "Помоги с автоматизацией",
        "Что ты умеешь?"
    ]
    
    print("🧪 Тестирование модуля:")
    print("=" * 50)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        result = module.handle(request)
        
        if result.get("success"):
            print(f"   ✅ Результат: {result.get('result', 'N/A')}")
            print(f"   💡 Объяснение: {result.get('explanation', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'N/A')}")
    
    print(f"\n📋 Информация о модуле:")
    info = module.get_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
