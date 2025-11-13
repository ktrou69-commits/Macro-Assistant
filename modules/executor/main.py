#!/usr/bin/env python3
"""
⚡ Executor Module - Выполнение .atlas макросов
Интегрирует DSL Engine и Vision Engine для выполнения автоматизации
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

class Executor:
    """
    Модуль выполнения макросов
    Интегрирует все движки автоматизации
    """
    
    def __init__(self):
        """Инициализация модуля выполнения"""
        # Ленивая загрузка движков
        self.atlas_parser = None
        self.atlas_executor = None
        self.template_matcher = None
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("executor")
        except ImportError:
            import logging
            self.logger = logging.getLogger("executor")
        
        self.logger.info("⚡ Executor модуль инициализирован")
    
    def _lazy_load_engines(self):
        """Ленивая загрузка движков"""
        if self.atlas_parser is None:
            from engines.dsl.atlas_parser import AtlasParser
            from engines.dsl.atlas_executor import AtlasExecutor
            from engines.vision.template_matcher import TemplateMatcher
            
            self.atlas_parser = AtlasParser()
            self.atlas_executor = AtlasExecutor()
            self.template_matcher = TemplateMatcher()
            
            self.logger.debug("🔧 Движки загружены")
    
    def handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обработка запроса на выполнение макроса
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            
        Returns:
            Результат выполнения
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"⚡ Выполнение запроса: {user_input[:50]}...")
            
            # Загружаем движки
            self._lazy_load_engines()
            
            # Определяем тип запроса
            if self._is_atlas_file_request(user_input):
                return self._execute_atlas_file(user_input, context, start_time)
            elif self._is_atlas_code_request(user_input, context):
                return self._execute_atlas_code(user_input, context, start_time)
            else:
                return self._format_error_response("Неизвестный тип запроса на выполнение", start_time)
        
        except Exception as e:
            self.logger.exception(f"❌ Ошибка выполнения: {e}")
            return self._format_error_response(str(e), start_time)
    
    def _is_atlas_file_request(self, user_input: str) -> bool:
        """Проверка запроса на выполнение .atlas файла"""
        return (
            "выполни" in user_input.lower() and 
            ".atlas" in user_input.lower()
        ) or (
            "execute" in user_input.lower() and
            ".atlas" in user_input.lower()
        )
    
    def _is_atlas_code_request(self, user_input: str, context: Optional[Dict[str, Any]]) -> bool:
        """Проверка запроса на выполнение .atlas кода"""
        return (
            context and 
            "atlas_code" in context and
            context["atlas_code"]
        )
    
    def _execute_atlas_file(self, user_input: str, context: Optional[Dict[str, Any]], 
                           start_time: float) -> Dict[str, Any]:
        """Выполнение .atlas файла"""
        try:
            # Извлекаем имя файла из запроса
            file_name = self._extract_file_name(user_input)
            
            if not file_name:
                return self._format_error_response("Не удалось определить имя файла", start_time)
            
            # Ищем файл
            file_path = self._find_atlas_file(file_name)
            
            if not file_path:
                return self._format_error_response(f"Файл {file_name} не найден", start_time)
            
            # Парсим и выполняем
            macro = self.atlas_parser.parse_file(file_path)
            result = self.atlas_executor.execute_macro(macro)
            
            execution_time = time.time() - start_time
            
            if result.success:
                return {
                    "success": True,
                    "result": f"Макрос {file_name} выполнен успешно",
                    "execution_time": execution_time,
                    "macro_info": {
                        "title": macro.title,
                        "description": macro.description,
                        "commands_count": len(macro.commands),
                        "file_path": str(file_path)
                    },
                    "performance": {
                        "macro_execution_time": result.execution_time,
                        "total_time": execution_time
                    },
                    "metadata": {
                        "module": "executor",
                        "type": "atlas_file_execution"
                    }
                }
            else:
                return self._format_error_response(f"Ошибка выполнения макроса: {result.message}", start_time)
        
        except Exception as e:
            return self._format_error_response(f"Ошибка выполнения файла: {e}", start_time)
    
    def _execute_atlas_code(self, user_input: str, context: Dict[str, Any], 
                           start_time: float) -> Dict[str, Any]:
        """Выполнение .atlas кода из контекста"""
        try:
            atlas_code = context["atlas_code"]
            
            # Парсим и выполняем код
            macro = self.atlas_parser.parse_content(atlas_code)
            result = self.atlas_executor.execute_macro(macro)
            
            execution_time = time.time() - start_time
            
            if result.success:
                return {
                    "success": True,
                    "result": "Atlas код выполнен успешно",
                    "execution_time": execution_time,
                    "macro_info": {
                        "title": macro.title,
                        "description": macro.description,
                        "commands_count": len(macro.commands)
                    },
                    "performance": {
                        "macro_execution_time": result.execution_time,
                        "total_time": execution_time
                    },
                    "metadata": {
                        "module": "executor",
                        "type": "atlas_code_execution"
                    }
                }
            else:
                return self._format_error_response(f"Ошибка выполнения кода: {result.message}", start_time)
        
        except Exception as e:
            return self._format_error_response(f"Ошибка выполнения кода: {e}", start_time)
    
    def _extract_file_name(self, user_input: str) -> Optional[str]:
        """Извлечение имени файла из запроса"""
        import re
        
        # Ищем паттерны типа "выполни file.atlas" или "execute file.atlas"
        patterns = [
            r'выполни\s+([^\s]+\.atlas)',
            r'execute\s+([^\s]+\.atlas)',
            r'запусти\s+([^\s]+\.atlas)',
            r'run\s+([^\s]+\.atlas)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Ищем любое упоминание .atlas файла
        atlas_match = re.search(r'([^\s]+\.atlas)', user_input, re.IGNORECASE)
        if atlas_match:
            return atlas_match.group(1)
        
        return None
    
    def _find_atlas_file(self, file_name: str) -> Optional[Path]:
        """Поиск .atlas файла в системе"""
        # Возможные директории для поиска
        search_dirs = [
            Path("data/generated_macros"),
            Path("macros/production"),
            Path("macros/examples"),
            Path(".")
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                # Прямой поиск
                file_path = search_dir / file_name
                if file_path.exists():
                    return file_path
                
                # Поиск без расширения
                if not file_name.endswith('.atlas'):
                    file_path = search_dir / f"{file_name}.atlas"
                    if file_path.exists():
                        return file_path
                
                # Рекурсивный поиск
                for atlas_file in search_dir.rglob("*.atlas"):
                    if atlas_file.name == file_name:
                        return atlas_file
        
        return None
    
    def _format_error_response(self, error: str, start_time: float) -> Dict[str, Any]:
        """Форматирование ответа об ошибке"""
        return {
            "success": False,
            "error": error,
            "execution_time": time.time() - start_time,
            "metadata": {
                "module": "executor",
                "type": "error"
            }
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Информация о модуле"""
        return {
            "name": "executor",
            "description": "Модуль выполнения .atlas макросов",
            "version": "1.0.0",
            "capabilities": [
                "Выполнение .atlas файлов",
                "Выполнение .atlas кода",
                "Computer Vision поиск",
                "Selenium автоматизация",
                "Системные команды"
            ],
            "engines": {
                "atlas_parser": self.atlas_parser is not None,
                "atlas_executor": self.atlas_executor is not None,
                "template_matcher": self.template_matcher is not None
            },
            "status": "ready"
        }

# Пример использования
if __name__ == "__main__":
    executor = Executor()
    
    test_requests = [
        "выполни chrome_new_tab.atlas",
        "execute test_macro.atlas"
    ]
    
    print("🧪 Тестирование Executor Module")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        
        result = executor.handle(request)
        
        if result["success"]:
            print(f"   ✅ Успех: {result['result']}")
            print(f"   ⚡ Время: {result['execution_time']:.3f}с")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    print(f"\n📊 Информация о модуле:")
    info = executor.get_info()
    print(f"   Название: {info['name']}")
    print(f"   Версия: {info['version']}")
    print(f"   Движки: {info['engines']}")
    
    print("\n⚡ Executor Module готов к работе!")
