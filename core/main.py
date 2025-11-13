#!/usr/bin/env python3
"""
🚀 Главный файл запуска Macro-Assistant
Точка входа в систему автоматизации
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import get_config
from core.logger import get_logger, LogContext
from core.ai_router import get_router
from core.context_manager import get_context_manager

class MacroAssistant:
    """
    Главный класс системы Macro-Assistant
    Координирует работу всех компонентов
    """
    
    def __init__(self):
        """Инициализация системы"""
        self.config = get_config()
        self.logger = get_logger("macro_assistant")
        self.router = get_router()
        self.context_manager = get_context_manager()
        
        self.logger.info("🚀 Macro-Assistant инициализируется...")
        
        # Проверяем конфигурацию
        self._validate_config()
        
        # Инициализируем компоненты
        self._initialize_components()
        
        self.logger.info("✅ Macro-Assistant готов к работе!")
    
    def _validate_config(self):
        """Валидация конфигурации"""
        with LogContext(self.logger, "Валидация конфигурации"):
            # Проверяем API ключи
            if not self.config.ai.api_key:
                self.logger.warning("⚠️ API ключ для AI не настроен")
            
            # Проверяем директории
            required_dirs = [
                self.config.paths.data,
                self.config.paths.logs,
                self.config.paths.cache,
                self.config.paths.templates
            ]
            
            for directory in required_dirs:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    self.logger.debug(f"Создана директория: {directory}")
    
    def _initialize_components(self):
        """Инициализация компонентов системы"""
        with LogContext(self.logger, "Инициализация компонентов"):
            # Статистика роутера
            router_stats = self.router.get_routing_stats()
            self.logger.info(f"📡 Роутер: {router_stats['loaded_modules']} модулей")
            
            # Статистика контекста
            context_stats = self.context_manager.get_stats()
            self.logger.info(f"💾 Контекст: {context_stats['variables_count']} переменных")
            
            # Очистка устаревших данных
            self.context_manager.cleanup()
    
    async def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обработка запроса пользователя
        
        Args:
            user_input: Ввод пользователя
            context: Дополнительный контекст
            
        Returns:
            Результат обработки
        """
        start_time = asyncio.get_event_loop().time()
        
        with LogContext(self.logger, f"Обработка запроса: {user_input[:50]}..."):
            try:
                # 1. Роутинг запроса
                routing_result = self.router.route(user_input, context)
                self.logger.info(f"🎯 Выбран модуль: {routing_result.module} ({routing_result.confidence:.2f})")
                
                # 2. Создание контекста выполнения
                execution_id = self.context_manager.create_execution_context(
                    user_input=user_input,
                    module=routing_result.module,
                    variables=context or {},
                    metadata={
                        "routing_method": routing_result.method,
                        "routing_confidence": routing_result.confidence
                    }
                )
                
                # 3. Загрузка и выполнение модуля
                module_result = await self._execute_module(
                    module_name=routing_result.module,
                    user_input=user_input,
                    execution_id=execution_id,
                    context=context
                )
                
                # 4. Обработка результата
                execution_time = asyncio.get_event_loop().time() - start_time
                
                # Добавляем в историю
                self.context_manager.add_history_entry(
                    user_input=user_input,
                    module=routing_result.module,
                    result=module_result,
                    execution_time=execution_time,
                    success=module_result.get("success", False),
                    error=module_result.get("error")
                )
                
                # Завершаем контекст выполнения
                self.context_manager.finish_execution_context(execution_id)
                
                # Формируем итоговый результат
                final_result = {
                    "success": module_result.get("success", False),
                    "result": module_result.get("result"),
                    "module": routing_result.module,
                    "execution_time": execution_time,
                    "routing": {
                        "confidence": routing_result.confidence,
                        "method": routing_result.method,
                        "matched_keywords": routing_result.matched_keywords
                    },
                    "metadata": module_result.get("metadata", {})
                }
                
                if module_result.get("error"):
                    final_result["error"] = module_result["error"]
                
                self.logger.info(f"✅ Запрос обработан за {execution_time:.3f}с")
                return final_result
                
            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                self.logger.exception(f"❌ Ошибка обработки запроса: {e}")
                
                return {
                    "success": False,
                    "error": str(e),
                    "execution_time": execution_time,
                    "module": "unknown"
                }
    
    async def _execute_module(self, module_name: str, user_input: str, 
                            execution_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Выполнение модуля
        
        Args:
            module_name: Имя модуля
            user_input: Ввод пользователя
            execution_id: ID контекста выполнения
            context: Контекст выполнения
            
        Returns:
            Результат выполнения модуля
        """
        try:
            # Динамическая загрузка модуля
            module = await self._load_module(module_name)
            
            if not module:
                return {
                    "success": False,
                    "error": f"Модуль {module_name} не найден или не может быть загружен"
                }
            
            # Подготовка контекста для модуля
            module_context = context or {}
            module_context.update({
                "execution_id": execution_id,
                "config": self.config.get_module_config(module_name),
                "global_variables": self.context_manager.list_variables("global")
            })
            
            # Выполнение модуля
            self.logger.debug(f"🔄 Выполнение модуля {module_name}")
            result = module.handle(user_input, module_context)
            
            # Обновляем контекст выполнения
            if isinstance(result, dict) and "variables" in result:
                self.context_manager.update_execution_context(
                    execution_id,
                    variables=result["variables"]
                )
            
            return result
            
        except Exception as e:
            self.logger.exception(f"❌ Ошибка выполнения модуля {module_name}: {e}")
            return {
                "success": False,
                "error": f"Ошибка выполнения модуля {module_name}: {str(e)}"
            }
    
    async def _load_module(self, module_name: str):
        """
        Динамическая загрузка модуля
        
        Args:
            module_name: Имя модуля
            
        Returns:
            Экземпляр модуля или None
        """
        try:
            # Импортируем модуль динамически
            module_path = f"modules.{module_name}.main"
            module_module = __import__(module_path, fromlist=[''])
            
            # Ищем класс модуля
            class_name = ''.join(word.capitalize() for word in module_name.split('_'))
            
            if hasattr(module_module, class_name):
                module_class = getattr(module_module, class_name)
                return module_class()
            else:
                self.logger.error(f"Класс {class_name} не найден в модуле {module_name}")
                return None
                
        except ImportError as e:
            self.logger.error(f"Не удалось импортировать модуль {module_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля {module_name}: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "status": "running",
            "version": "1.0.0",
            "config": {
                "debug": self.config.system.debug,
                "ai_model": self.config.ai.model,
                "cache_enabled": self.config.system.cache_enabled
            },
            "router": self.router.get_routing_stats(),
            "context": self.context_manager.get_stats(),
            "uptime": "N/A"  # TODO: Добавить отслеживание времени работы
        }
    
    def shutdown(self):
        """Корректное завершение работы системы"""
        with LogContext(self.logger, "Завершение работы системы"):
            # Очистка кэшей
            self.router.clear_cache()
            
            # Сохранение данных контекста
            if hasattr(self.context_manager, '_save_variables'):
                self.context_manager._save_variables()
                self.context_manager._save_history()
                self.context_manager._save_session()
            
            self.logger.info("👋 Macro-Assistant завершил работу")

# CLI интерфейс
async def cli_interface():
    """Простой CLI интерфейс для тестирования"""
    assistant = MacroAssistant()
    
    print("\n🚀 Macro-Assistant CLI")
    print("=" * 50)
    print("Введите команды или 'exit' для выхода")
    print("Примеры:")
    print("  - найди на YouTube видео про Python")
    print("  - открой калькулятор")
    print("  - создай переменную test")
    print("=" * 50)
    
    try:
        while True:
            try:
                user_input = input("\n💬 Команда: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    break
                
                if user_input.lower() == 'status':
                    status = assistant.get_system_status()
                    print(f"📊 Статус системы: {status}")
                    continue
                
                if not user_input:
                    continue
                
                # Обработка запроса
                result = await assistant.process_request(user_input)
                
                # Вывод результата
                if result["success"]:
                    print(f"✅ Результат: {result.get('result', 'Выполнено')}")
                    print(f"🎯 Модуль: {result['module']}")
                    print(f"⚡ Время: {result['execution_time']:.3f}с")
                else:
                    print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Прерывание пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    finally:
        assistant.shutdown()

def main():
    """Главная функция"""
    try:
        # Запуск CLI интерфейса
        asyncio.run(cli_interface())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
