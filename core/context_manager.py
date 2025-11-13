#!/usr/bin/env python3
"""
💾 Менеджер контекста для Macro-Assistant
Управление состоянием, переменными и историей выполнения
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from threading import Lock

@dataclass
class ExecutionContext:
    """Контекст выполнения команды"""
    user_input: str
    module: str
    timestamp: datetime
    execution_id: str
    variables: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class HistoryEntry:
    """Запись в истории выполнения"""
    timestamp: datetime
    user_input: str
    module: str
    result: Dict[str, Any]
    execution_time: float
    success: bool
    error: Optional[str] = None

class ContextManager:
    """
    Менеджер контекста системы
    Управляет переменными, историей и состоянием выполнения
    """
    
    def __init__(self, persist_to_disk: bool = True):
        """
        Инициализация менеджера контекста
        
        Args:
            persist_to_disk: Сохранять ли данные на диск
        """
        self.persist_to_disk = persist_to_disk
        self._lock = Lock()
        
        # Основные хранилища данных
        self._variables: Dict[str, Any] = {}
        self._history: List[HistoryEntry] = []
        self._active_contexts: Dict[str, ExecutionContext] = {}
        self._session_data: Dict[str, Any] = {}
        
        # Настройки
        self.max_history_entries = 1000
        self.max_variable_age_days = 30
        self.auto_cleanup_interval = 3600  # 1 час
        
        # Пути к файлам
        try:
            from .config import get_config
            config = get_config()
            self.data_dir = config.paths.data
        except ImportError:
            self.data_dir = Path("data")
        
        self.variables_file = self.data_dir / "variables.json"
        self.history_file = self.data_dir / "history.json"
        self.session_file = self.data_dir / "session.json"
        
        # Создаем директории
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Настраиваем логгер (до загрузки данных)
        try:
            from .logger import get_logger
            self.logger = get_logger("context_manager")
        except ImportError:
            import logging
            self.logger = logging.getLogger("context_manager")
        
        # Загружаем данные
        if self.persist_to_disk:
            self._load_from_disk()
    
    # === Управление переменными ===
    
    def set_variable(self, name: str, value: Any, scope: str = "global", ttl: Optional[int] = None):
        """
        Установка переменной
        
        Args:
            name: Имя переменной
            value: Значение
            scope: Область видимости (global, session, temporary)
            ttl: Время жизни в секундах (опционально)
        """
        with self._lock:
            variable_data = {
                "value": value,
                "scope": scope,
                "created_at": datetime.now().isoformat(),
                "ttl": ttl,
                "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl else None
            }
            
            self._variables[name] = variable_data
            
            if self.persist_to_disk and scope == "global":
                self._save_variables()
            
            self.logger.debug(f"Переменная установлена: {name} = {value} (scope: {scope})")
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Получение переменной
        
        Args:
            name: Имя переменной
            default: Значение по умолчанию
            
        Returns:
            Значение переменной или default
        """
        with self._lock:
            if name not in self._variables:
                return default
            
            variable_data = self._variables[name]
            
            # Проверяем TTL
            if variable_data.get("expires_at"):
                expires_at = datetime.fromisoformat(variable_data["expires_at"])
                if datetime.now() > expires_at:
                    del self._variables[name]
                    self.logger.debug(f"Переменная {name} истекла и удалена")
                    return default
            
            return variable_data["value"]
    
    def delete_variable(self, name: str) -> bool:
        """
        Удаление переменной
        
        Args:
            name: Имя переменной
            
        Returns:
            True если переменная была удалена
        """
        with self._lock:
            if name in self._variables:
                scope = self._variables[name]["scope"]
                del self._variables[name]
                
                if self.persist_to_disk and scope == "global":
                    self._save_variables()
                
                self.logger.debug(f"Переменная удалена: {name}")
                return True
            return False
    
    def list_variables(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Получение списка переменных
        
        Args:
            scope: Фильтр по области видимости
            
        Returns:
            Словарь переменных
        """
        with self._lock:
            result = {}
            for name, data in self._variables.items():
                if scope is None or data["scope"] == scope:
                    # Проверяем TTL
                    if data.get("expires_at"):
                        expires_at = datetime.fromisoformat(data["expires_at"])
                        if datetime.now() > expires_at:
                            continue
                    
                    result[name] = {
                        "value": data["value"],
                        "scope": data["scope"],
                        "created_at": data["created_at"]
                    }
            return result
    
    # === Управление историей ===
    
    def add_history_entry(self, user_input: str, module: str, result: Dict[str, Any], 
                         execution_time: float, success: bool, error: Optional[str] = None):
        """
        Добавление записи в историю
        
        Args:
            user_input: Ввод пользователя
            module: Использованный модуль
            result: Результат выполнения
            execution_time: Время выполнения
            success: Успешность выполнения
            error: Ошибка (если есть)
        """
        with self._lock:
            entry = HistoryEntry(
                timestamp=datetime.now(),
                user_input=user_input,
                module=module,
                result=result,
                execution_time=execution_time,
                success=success,
                error=error
            )
            
            self._history.append(entry)
            
            # Ограничиваем размер истории
            if len(self._history) > self.max_history_entries:
                self._history = self._history[-self.max_history_entries:]
            
            if self.persist_to_disk:
                self._save_history()
            
            self.logger.debug(f"Добавлена запись в историю: {user_input[:50]}...")
    
    def get_history(self, limit: int = 50, module: Optional[str] = None, 
                   success_only: bool = False) -> List[Dict[str, Any]]:
        """
        Получение истории выполнения
        
        Args:
            limit: Максимальное количество записей
            module: Фильтр по модулю
            success_only: Только успешные выполнения
            
        Returns:
            Список записей истории
        """
        with self._lock:
            filtered_history = []
            
            for entry in reversed(self._history):
                if module and entry.module != module:
                    continue
                if success_only and not entry.success:
                    continue
                
                filtered_history.append({
                    "timestamp": entry.timestamp.isoformat(),
                    "user_input": entry.user_input,
                    "module": entry.module,
                    "result": entry.result,
                    "execution_time": entry.execution_time,
                    "success": entry.success,
                    "error": entry.error
                })
                
                if len(filtered_history) >= limit:
                    break
            
            return filtered_history
    
    def clear_history(self, older_than_days: Optional[int] = None):
        """
        Очистка истории
        
        Args:
            older_than_days: Удалить записи старше N дней (опционально)
        """
        with self._lock:
            if older_than_days:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
                self._history = [entry for entry in self._history if entry.timestamp > cutoff_date]
                self.logger.info(f"Удалены записи истории старше {older_than_days} дней")
            else:
                self._history.clear()
                self.logger.info("История полностью очищена")
            
            if self.persist_to_disk:
                self._save_history()
    
    # === Управление контекстами выполнения ===
    
    def create_execution_context(self, user_input: str, module: str, 
                               variables: Optional[Dict[str, Any]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Создание контекста выполнения
        
        Args:
            user_input: Ввод пользователя
            module: Модуль для выполнения
            variables: Переменные контекста
            metadata: Метаданные
            
        Returns:
            ID контекста выполнения
        """
        execution_id = f"{module}_{int(time.time() * 1000)}"
        
        context = ExecutionContext(
            user_input=user_input,
            module=module,
            timestamp=datetime.now(),
            execution_id=execution_id,
            variables=variables or {},
            metadata=metadata or {}
        )
        
        with self._lock:
            self._active_contexts[execution_id] = context
        
        self.logger.debug(f"Создан контекст выполнения: {execution_id}")
        return execution_id
    
    def get_execution_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """
        Получение контекста выполнения
        
        Args:
            execution_id: ID контекста
            
        Returns:
            Контекст выполнения или None
        """
        with self._lock:
            return self._active_contexts.get(execution_id)
    
    def update_execution_context(self, execution_id: str, **updates):
        """
        Обновление контекста выполнения
        
        Args:
            execution_id: ID контекста
            **updates: Обновления для контекста
        """
        with self._lock:
            if execution_id in self._active_contexts:
                context = self._active_contexts[execution_id]
                for key, value in updates.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                    elif key == "variables":
                        context.variables.update(value)
                    elif key == "metadata":
                        context.metadata.update(value)
    
    def finish_execution_context(self, execution_id: str):
        """
        Завершение контекста выполнения
        
        Args:
            execution_id: ID контекста
        """
        with self._lock:
            if execution_id in self._active_contexts:
                del self._active_contexts[execution_id]
                self.logger.debug(f"Контекст выполнения завершен: {execution_id}")
    
    # === Сессионные данные ===
    
    def set_session_data(self, key: str, value: Any):
        """Установка сессионных данных"""
        with self._lock:
            self._session_data[key] = value
            if self.persist_to_disk:
                self._save_session()
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Получение сессионных данных"""
        with self._lock:
            return self._session_data.get(key, default)
    
    # === Сохранение/загрузка ===
    
    def _save_variables(self):
        """Сохранение переменных на диск"""
        try:
            # Фильтруем только глобальные переменные
            global_vars = {
                name: data for name, data in self._variables.items()
                if data["scope"] == "global"
            }
            
            with open(self.variables_file, 'w', encoding='utf-8') as f:
                json.dump(global_vars, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения переменных: {e}")
    
    def _save_history(self):
        """Сохранение истории на диск"""
        try:
            history_data = []
            for entry in self._history:
                history_data.append({
                    "timestamp": entry.timestamp.isoformat(),
                    "user_input": entry.user_input,
                    "module": entry.module,
                    "result": entry.result,
                    "execution_time": entry.execution_time,
                    "success": entry.success,
                    "error": entry.error
                })
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения истории: {e}")
    
    def _save_session(self):
        """Сохранение сессионных данных"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self._session_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения сессии: {e}")
    
    def _load_from_disk(self):
        """Загрузка данных с диска"""
        # Загрузка переменных
        if self.variables_file.exists():
            try:
                with open(self.variables_file, 'r', encoding='utf-8') as f:
                    self._variables = json.load(f)
                self.logger.debug(f"Загружено {len(self._variables)} переменных")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки переменных: {e}")
        
        # Загрузка истории
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                self._history = []
                for entry_data in history_data:
                    entry = HistoryEntry(
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        user_input=entry_data["user_input"],
                        module=entry_data["module"],
                        result=entry_data["result"],
                        execution_time=entry_data["execution_time"],
                        success=entry_data["success"],
                        error=entry_data.get("error")
                    )
                    self._history.append(entry)
                
                self.logger.debug(f"Загружено {len(self._history)} записей истории")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки истории: {e}")
        
        # Загрузка сессионных данных
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self._session_data = json.load(f)
                self.logger.debug(f"Загружено {len(self._session_data)} сессионных данных")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки сессии: {e}")
    
    def cleanup(self):
        """Очистка устаревших данных"""
        with self._lock:
            # Очистка переменных с истекшим TTL
            expired_vars = []
            for name, data in self._variables.items():
                if data.get("expires_at"):
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    if datetime.now() > expires_at:
                        expired_vars.append(name)
            
            for name in expired_vars:
                del self._variables[name]
            
            if expired_vars:
                self.logger.info(f"Удалено {len(expired_vars)} устаревших переменных")
                if self.persist_to_disk:
                    self._save_variables()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики контекста"""
        with self._lock:
            return {
                "variables_count": len(self._variables),
                "history_entries": len(self._history),
                "active_contexts": len(self._active_contexts),
                "session_data_keys": len(self._session_data),
                "last_execution": self._history[-1].timestamp.isoformat() if self._history else None
            }

# Глобальный экземпляр менеджера контекста
_context_manager: Optional[ContextManager] = None

def get_context_manager() -> ContextManager:
    """Получение глобального менеджера контекста"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager

# Пример использования
if __name__ == "__main__":
    cm = get_context_manager()
    
    print("💾 Тестирование менеджера контекста")
    
    # Тест переменных
    cm.set_variable("test_var", "Hello World", scope="global")
    cm.set_variable("temp_var", "Temporary", scope="temporary", ttl=5)
    
    print(f"test_var: {cm.get_variable('test_var')}")
    print(f"temp_var: {cm.get_variable('temp_var')}")
    
    # Тест истории
    cm.add_history_entry(
        user_input="Тестовая команда",
        module="test_module",
        result={"success": True, "message": "OK"},
        execution_time=0.5,
        success=True
    )
    
    # Тест контекста выполнения
    ctx_id = cm.create_execution_context(
        user_input="Создать макрос",
        module="macro_generator",
        variables={"user": "test"},
        metadata={"version": "1.0"}
    )
    
    print(f"Создан контекст: {ctx_id}")
    
    # Статистика
    stats = cm.get_stats()
    print(f"Статистика: {stats}")
    
    cm.finish_execution_context(ctx_id)
