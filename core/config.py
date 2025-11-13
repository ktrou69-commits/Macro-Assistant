#!/usr/bin/env python3
"""
⚙️ Конфигурация системы Macro-Assistant
Централизованное управление настройками
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class AIConfig:
    """Конфигурация AI модели"""
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    base_url: Optional[str] = None

@dataclass
class SystemConfig:
    """Системные настройки"""
    debug: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_ttl: int = 3600
    sandbox_mode: bool = True
    max_execution_time: int = 300

@dataclass
class PathConfig:
    """Пути к директориям"""
    root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    templates: Path = field(default_factory=lambda: Path("templates"))
    data: Path = field(default_factory=lambda: Path("data"))
    logs: Path = field(default_factory=lambda: Path("data/logs"))
    cache: Path = field(default_factory=lambda: Path("data/cache"))
    modules: Path = field(default_factory=lambda: Path("modules"))

@dataclass
class VoiceConfig:
    """Настройки голосового управления"""
    enabled: bool = True
    activation_phrase: str = "эй макро"
    language: str = "ru-RU"
    timeout: int = 5
    continuous_listening: bool = True

@dataclass
class GUIConfig:
    """Настройки интерфейса"""
    theme: str = "dark"
    window_size: str = "1200x800"
    minimize_to_tray: bool = True
    show_notifications: bool = True

class Config:
    """
    Главный класс конфигурации системы
    Загружает настройки из переменных окружения и файлов
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Инициализация конфигурации
        
        Args:
            config_file: Путь к файлу конфигурации (опционально)
        """
        self.config_file = config_file or Path(".env")
        self._load_env_variables()
        
        # Инициализация подконфигураций
        self.ai = self._init_ai_config()
        self.system = self._init_system_config()
        self.paths = self._init_path_config()
        self.voice = self._init_voice_config()
        self.gui = self._init_gui_config()
        
        # Создание необходимых директорий
        self._ensure_directories()
    
    def _load_env_variables(self):
        """Загрузка переменных окружения из .env файла"""
        try:
            from dotenv import load_dotenv
            if self.config_file.exists():
                load_dotenv(self.config_file)
        except ImportError:
            # dotenv не установлен, используем только системные переменные
            pass
    
    def _init_ai_config(self) -> AIConfig:
        """Инициализация AI конфигурации"""
        return AIConfig(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
    
    def _init_system_config(self) -> SystemConfig:
        """Инициализация системной конфигурации"""
        return SystemConfig(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            sandbox_mode=os.getenv("SANDBOX_MODE", "true").lower() == "true",
            max_execution_time=int(os.getenv("MAX_EXECUTION_TIME", "300"))
        )
    
    def _init_path_config(self) -> PathConfig:
        """Инициализация путей"""
        root = Path(__file__).parent.parent
        
        return PathConfig(
            root=root,
            templates=Path(os.getenv("TEMPLATES_PATH", "templates")),
            data=Path(os.getenv("DATA_PATH", "data")),
            logs=Path(os.getenv("LOGS_PATH", "data/logs")),
            cache=Path(os.getenv("CACHE_PATH", "data/cache")),
            modules=Path(os.getenv("MODULES_PATH", "modules"))
        )
    
    def _init_voice_config(self) -> VoiceConfig:
        """Инициализация голосовой конфигурации"""
        return VoiceConfig(
            enabled=os.getenv("VOICE_ENABLED", "true").lower() == "true",
            activation_phrase=os.getenv("VOICE_ACTIVATION_PHRASE", "эй макро"),
            language=os.getenv("VOICE_LANGUAGE", "ru-RU"),
            timeout=int(os.getenv("VOICE_TIMEOUT", "5")),
            continuous_listening=os.getenv("VOICE_CONTINUOUS", "true").lower() == "true"
        )
    
    def _init_gui_config(self) -> GUIConfig:
        """Инициализация GUI конфигурации"""
        return GUIConfig(
            theme=os.getenv("GUI_THEME", "dark"),
            window_size=os.getenv("GUI_WINDOW_SIZE", "1200x800"),
            minimize_to_tray=os.getenv("GUI_MINIMIZE_TO_TRAY", "true").lower() == "true",
            show_notifications=os.getenv("GUI_SHOW_NOTIFICATIONS", "true").lower() == "true"
        )
    
    def _ensure_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.paths.data,
            self.paths.logs,
            self.paths.cache,
            self.paths.templates
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Получение конфигурации конкретного модуля
        
        Args:
            module_name: Имя модуля
            
        Returns:
            Конфигурация модуля
        """
        config_path = self.paths.modules / module_name / "config.json"
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфига модуля {module_name}: {e}")
            return {}
    
    def save_module_config(self, module_name: str, config: Dict[str, Any]):
        """
        Сохранение конфигурации модуля
        
        Args:
            module_name: Имя модуля
            config: Конфигурация для сохранения
        """
        config_path = self.paths.modules / module_name / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения конфига модуля {module_name}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование конфигурации в словарь"""
        return {
            "ai": {
                "model": self.ai.model,
                "temperature": self.ai.temperature,
                "max_tokens": self.ai.max_tokens,
                "timeout": self.ai.timeout
            },
            "system": {
                "debug": self.system.debug,
                "log_level": self.system.log_level,
                "cache_enabled": self.system.cache_enabled,
                "sandbox_mode": self.system.sandbox_mode
            },
            "voice": {
                "enabled": self.voice.enabled,
                "activation_phrase": self.voice.activation_phrase,
                "language": self.voice.language
            },
            "gui": {
                "theme": self.gui.theme,
                "window_size": self.gui.window_size
            }
        }
    
    def __repr__(self) -> str:
        """Строковое представление конфигурации"""
        return f"Config(ai_model={self.ai.model}, debug={self.system.debug})"

# Глобальный экземпляр конфигурации
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """
    Получение глобального экземпляра конфигурации
    
    Returns:
        Экземпляр конфигурации
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def reload_config():
    """Перезагрузка конфигурации"""
    global _config_instance
    _config_instance = None
    return get_config()

# Пример использования
if __name__ == "__main__":
    config = get_config()
    
    print("🔧 Конфигурация Macro-Assistant:")
    print(f"   AI Model: {config.ai.model}")
    print(f"   Debug: {config.system.debug}")
    print(f"   Cache: {config.system.cache_enabled}")
    print(f"   Voice: {config.voice.enabled}")
    print(f"   Root Path: {config.paths.root}")
    
    # Тест конфигурации модуля
    test_config = {"test": True, "version": "1.0"}
    config.save_module_config("test_module", test_config)
    loaded_config = config.get_module_config("test_module")
    print(f"   Test Module Config: {loaded_config}")
