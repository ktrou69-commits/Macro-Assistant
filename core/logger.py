#!/usr/bin/env python3
"""
📝 Система логирования для Macro-Assistant
Централизованное логирование с ротацией и форматированием
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консольного вывода"""
    
    # ANSI цветовые коды
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        if record.levelname in self.COLORS:
            record.levelname_colored = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )
        else:
            record.levelname_colored = record.levelname
        
        return super().format(record)

class MacroAssistantLogger:
    """
    Главный класс логгера для Macro-Assistant
    """
    
    def __init__(self, name: str = "macro_assistant"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        # Очищаем существующие хэндлеры
        self.logger.handlers.clear()
        
        # Получаем конфигурацию
        try:
            from .config import get_config
            config = get_config()
            log_level = getattr(logging, config.system.log_level.upper(), logging.INFO)
            logs_dir = config.paths.logs
        except ImportError:
            log_level = logging.INFO
            logs_dir = Path("data/logs")
        
        # Устанавливаем уровень логирования
        self.logger.setLevel(log_level)
        
        # Создаем директорию для логов
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Консольный хэндлер с цветами
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname_colored)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
        
        # Файловый хэндлер с ротацией
        log_file = logs_dir / f"{self.name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # В файл пишем все
        
        # Добавляем хэндлеры
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Предотвращаем дублирование в родительских логгерах
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Отладочное сообщение"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Информационное сообщение"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Предупреждение"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Ошибка"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Критическая ошибка"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Ошибка с трассировкой стека"""
        self.logger.exception(message, **kwargs)

# Глобальные логгеры для разных компонентов
_loggers = {}

def get_logger(name: str = "macro_assistant") -> MacroAssistantLogger:
    """
    Получение логгера для компонента
    
    Args:
        name: Имя компонента
        
    Returns:
        Экземпляр логгера
    """
    if name not in _loggers:
        _loggers[name] = MacroAssistantLogger(name)
    return _loggers[name]

def setup_module_logger(module_name: str) -> MacroAssistantLogger:
    """
    Создание логгера для модуля
    
    Args:
        module_name: Имя модуля
        
    Returns:
        Логгер модуля
    """
    logger_name = f"module.{module_name}"
    return get_logger(logger_name)

def log_execution_time(func):
    """
    Декоратор для логирования времени выполнения функции
    
    Args:
        func: Функция для декорирования
        
    Returns:
        Декорированная функция
    """
    def wrapper(*args, **kwargs):
        logger = get_logger("performance")
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⚡ {func.__name__} выполнена за {execution_time:.3f}с")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {func.__name__} завершилась с ошибкой за {execution_time:.3f}с: {e}")
            raise
    
    return wrapper

def log_ai_request(func):
    """
    Декоратор для логирования AI запросов
    
    Args:
        func: Функция AI запроса
        
    Returns:
        Декорированная функция
    """
    def wrapper(*args, **kwargs):
        logger = get_logger("ai_requests")
        start_time = datetime.now()
        
        # Логируем начало запроса
        prompt_preview = str(args[0])[:100] if args else "No prompt"
        logger.info(f"🤖 AI запрос начат: {prompt_preview}...")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Логируем успешный результат
            result_preview = str(result)[:100] if result else "No result"
            logger.info(f"✅ AI запрос завершен за {execution_time:.3f}с: {result_preview}...")
            
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ AI запрос завершился с ошибкой за {execution_time:.3f}с: {e}")
            raise
    
    return wrapper

class LogContext:
    """Контекстный менеджер для логирования операций"""
    
    def __init__(self, logger: MacroAssistantLogger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"🔄 Начало операции: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"✅ Операция завершена: {self.operation} ({execution_time:.3f}с)")
        else:
            self.logger.error(f"❌ Операция завершилась с ошибкой: {self.operation} ({execution_time:.3f}с) - {exc_val}")

# Пример использования
if __name__ == "__main__":
    # Тестирование логгера
    logger = get_logger("test")
    
    logger.info("🚀 Тестирование системы логирования")
    logger.debug("Отладочное сообщение")
    logger.warning("⚠️ Предупреждение")
    logger.error("❌ Ошибка")
    
    # Тест контекстного менеджера
    with LogContext(logger, "Тестовая операция"):
        import time
        time.sleep(0.1)
        logger.info("Выполняется тестовая операция")
    
    # Тест декоратора
    @log_execution_time
    def test_function():
        import time
        time.sleep(0.05)
        return "Результат"
    
    result = test_function()
    logger.info(f"Результат функции: {result}")
    
    print("\n📝 Логи сохранены в data/logs/")
    print("🎨 Консольный вывод с цветами")
