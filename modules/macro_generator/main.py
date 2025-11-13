#!/usr/bin/env python3
"""
🎭 Macro Generator - Главный модуль генерации макросов
Создает .atlas макросы из естественного языка с помощью AI
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class GenerationResult:
    """Результат генерации макроса"""
    success: bool
    atlas_code: str
    title: str
    description: str
    category: str
    estimated_time: str
    commands_count: int
    metadata: Dict[str, Any]
    error: Optional[str] = None
    generation_time: float = 0.0

class MacroGenerator:
    """
    Главный класс генератора макросов
    Преобразует естественный язык в .atlas макросы
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Инициализация генератора макросов
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.module_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        
        # Загружаем компоненты
        self.base_prompt = self._load_base_prompt()
        self.generation_rules = self._load_generation_rules()
        self.few_shot_examples = self._load_few_shot_examples()
        
        # Кэш для ускорения
        self.templates_cache = {}
        self.selectors_cache = {}
        self.generation_cache = {}
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("macro_generator")
        except ImportError:
            import logging
            self.logger = logging.getLogger("macro_generator")
        
        self.logger.info("🎭 MacroGenerator инициализирован")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации модуля"""
        config_file = self.module_dir / config_path
        
        if not config_file.exists():
            self.logger.warning(f"⚠️ Конфиг не найден: {config_file}")
            return self._default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки конфига: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "name": "macro_generator",
            "ai_settings": {
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "max_tokens": 3000,
                "timeout": 45
            },
            "module_settings": {
                "cache_results": True,
                "enable_dsl_validation": True,
                "generate_metadata": True
            }
        }
    
    def _load_base_prompt(self) -> str:
        """Загрузка базового промпта"""
        prompt_file = self.module_dir / "prompts" / "base_prompt.txt"
        
        if not prompt_file.exists():
            self.logger.error(f"❌ Базовый промпт не найден: {prompt_file}")
            return "Ты эксперт по созданию макросов автоматизации."
        
        try:
            return prompt_file.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки промпта: {e}")
            return "Ты эксперт по созданию макросов автоматизации."
    
    def _load_generation_rules(self) -> Dict[str, Any]:
        """Загрузка правил генерации"""
        rules_file = self.module_dir / "rules" / "generation_rules.json"
        
        if not rules_file.exists():
            self.logger.warning(f"⚠️ Правила генерации не найдены: {rules_file}")
            return {}
        
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки правил: {e}")
            return {}
    
    def _load_few_shot_examples(self) -> Dict[str, Any]:
        """Загрузка примеров для Few-Shot Learning"""
        examples_file = self.module_dir / "examples" / "few_shot_examples.json"
        
        if not examples_file.exists():
            self.logger.warning(f"⚠️ Примеры не найдены: {examples_file}")
            return {}
        
        try:
            with open(examples_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки примеров: {e}")
            return {}
    
    def handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Основной метод обработки запроса
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            
        Returns:
            Результат генерации макроса
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🎭 Генерация макроса: {user_input[:50]}...")
            
            # Проверяем кэш
            cache_key = self._get_cache_key(user_input, context)
            if self.config["module_settings"].get("cache_results", True):
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    self.logger.debug("📋 Использован кэш")
                    return self._format_response(cached_result, time.time() - start_time)
            
            # Анализируем запрос
            intent_analysis = self._analyze_user_intent(user_input)
            self.logger.debug(f"🎯 Анализ намерений: {intent_analysis['category']}")
            
            # Подготавливаем контекст для AI
            ai_context = self._prepare_ai_context(user_input, context, intent_analysis)
            
            # Генерируем макрос через AI
            generation_result = self._generate_with_ai(ai_context)
            
            if not generation_result.success:
                return self._format_error_response(generation_result.error, time.time() - start_time)
            
            # Валидируем и улучшаем результат
            if self.config["module_settings"].get("enable_dsl_validation", True):
                generation_result = self._validate_and_improve(generation_result)
            
            # Сохраняем в кэш
            if self.config["module_settings"].get("cache_results", True):
                self._save_to_cache(cache_key, generation_result)
            
            # Сохраняем макрос в файл (опционально)
            if context and context.get("save_to_file", False):
                self._save_macro_to_file(generation_result, user_input)
            
            generation_result.generation_time = time.time() - start_time
            self.logger.info(f"✅ Макрос сгенерирован за {generation_result.generation_time:.3f}с")
            
            return self._format_response(generation_result, generation_result.generation_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.exception(f"❌ Ошибка генерации макроса: {e}")
            return self._format_error_response(str(e), execution_time)
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Анализ намерений пользователя
        
        Args:
            user_input: Ввод пользователя
            
        Returns:
            Анализ намерений
        """
        user_lower = user_input.lower()
        
        # Определяем категорию автоматизации
        if any(site in user_lower for site in ['youtube', 'google', 'twitter', 'facebook', 'github']):
            category = "web_automation"
        elif any(word in user_lower for word in ['калькулятор', 'calculator', 'посчитай', 'вычисли']):
            category = "calculator_automation"
        elif any(word in user_lower for word in ['найди файл', 'spotlight', 'поиск файл']):
            category = "spotlight_automation"
        elif any(word in user_lower for word in ['открой', 'запусти', 'приложение']):
            category = "system_automation"
        else:
            category = "mixed_automation"
        
        # Определяем сложность
        complexity = "simple"
        if len(user_input.split()) > 10 or any(word in user_lower for word in ['и', 'потом', 'затем', 'после']):
            complexity = "medium"
        if any(word in user_lower for word in ['цикл', 'повтори', 'если', 'условие', 'переменная']):
            complexity = "complex"
        
        # Извлекаем ключевые элементы
        keywords = self._extract_keywords(user_input)
        
        return {
            "category": category,
            "complexity": complexity,
            "keywords": keywords,
            "estimated_commands": self._estimate_commands_count(user_input, complexity),
            "requires_internet": self._requires_internet(user_input),
            "target_apps": self._extract_target_apps(user_input)
        }
    
    def _extract_keywords(self, user_input: str) -> List[str]:
        """Извлечение ключевых слов из запроса"""
        # Простое извлечение ключевых слов
        words = re.findall(r'\b\w+\b', user_input.lower())
        
        # Фильтруем значимые слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'из', 'к', 'у'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Ограничиваем количество
    
    def _estimate_commands_count(self, user_input: str, complexity: str) -> int:
        """Оценка количества команд в макросе"""
        base_count = len(user_input.split()) // 2
        
        multipliers = {
            "simple": 1.0,
            "medium": 1.5,
            "complex": 2.5
        }
        
        return max(3, int(base_count * multipliers.get(complexity, 1.0)))
    
    def _requires_internet(self, user_input: str) -> bool:
        """Проверка необходимости интернета"""
        web_indicators = ['youtube', 'google', 'twitter', 'сайт', 'браузер', 'интернет', 'поиск в']
        return any(indicator in user_input.lower() for indicator in web_indicators)
    
    def _extract_target_apps(self, user_input: str) -> List[str]:
        """Извлечение целевых приложений"""
        apps = []
        user_lower = user_input.lower()
        
        app_mapping = {
            'калькулятор': 'Calculator',
            'calculator': 'Calculator',
            'хром': 'ChromeApp',
            'chrome': 'ChromeApp',
            'сафари': 'Safari',
            'safari': 'Safari',
            'finder': 'Finder',
            'файндер': 'Finder'
        }
        
        for keyword, app in app_mapping.items():
            if keyword in user_lower:
                apps.append(app)
        
        return apps
    
    def _prepare_ai_context(self, user_input: str, context: Optional[Dict[str, Any]], 
                           intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Подготовка контекста для AI
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            intent_analysis: Анализ намерений
            
        Returns:
            Контекст для AI
        """
        # Получаем релевантные примеры
        examples = self._get_relevant_examples(intent_analysis["category"])
        
        # Подготавливаем списки доступных элементов
        templates_list = self._get_templates_list()
        dom_selectors = self._get_dom_selectors_list()
        system_apps = self._get_system_apps_list()
        
        # Формируем полный промпт
        try:
            full_prompt = self.base_prompt.format(
                templates_list=templates_list,
                dom_selectors=dom_selectors,
                system_apps=system_apps,
                user_input=user_input,
                context=json.dumps(context or {}, ensure_ascii=False, indent=2)
            )
        except KeyError as e:
            # Если в промпте отсутствуют некоторые переменные, используем базовый промпт
            self.logger.warning(f"⚠️ Переменная {e} не найдена в промпте, используем упрощенную версию")
            full_prompt = f"""Ты эксперт по созданию макросов автоматизации.

Создай .atlas макрос для запроса: "{user_input}"

Доступные команды:
- open <app> - открыть приложение
- click <element> - кликнуть
- type "text" - ввести текст  
- wait <time> - ждать
- selenium_init url="..." - открыть браузер
- selenium_click selector="..." - клик по селектору
- selenium_type selector="..." text="..." - ввод текста

Ответь в JSON формате:
{{
  "success": true,
  "atlas_code": "код макроса",
  "title": "название",
  "description": "описание",
  "category": "web_automation",
  "estimated_time": "5 секунд",
  "commands_count": 3,
  "metadata": {{"platform": "macOS"}}
}}"""
        
        return {
            "prompt": full_prompt,
            "examples": examples,
            "intent_analysis": intent_analysis,
            "user_input": user_input,
            "context": context or {}
        }
    
    def _get_relevant_examples(self, category: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Получение релевантных примеров для Few-Shot Learning"""
        examples_key = f"{category}_examples"
        
        if examples_key in self.few_shot_examples:
            examples = self.few_shot_examples[examples_key][:limit]
        else:
            # Используем общие примеры
            all_examples = []
            for key, value in self.few_shot_examples.items():
                if isinstance(value, list):
                    all_examples.extend(value)
            
            # Сортируем по релевантности (простая эвристика)
            examples = sorted(all_examples, key=lambda x: x.get("complexity", "simple"))[:limit]
        
        return examples
    
    def _get_templates_list(self) -> str:
        """Получение списка доступных шаблонов"""
        # TODO: Интеграция с template_parser модулем
        # Пока возвращаем заглушку
        return """
• ChromeApp-btn - Запуск Chrome
• ChromeNewTab-btn - Новая вкладка Chrome
• YouTube-Search-btn - Поиск на YouTube
• Calculator - Калькулятор
• Finder - Файловый менеджер
"""
    
    def _get_dom_selectors_list(self) -> str:
        """Получение списка DOM селекторов"""
        # TODO: Интеграция с selector_creator модулем
        return """
• input#search - Поле поиска YouTube
• button#search-icon-legacy - Кнопка поиска YouTube
• textarea[name='q'] - Поле поиска Google
• input[name='btnK'] - Кнопка поиска Google
"""
    
    def _get_system_apps_list(self) -> str:
        """Получение списка системных приложений"""
        return """
• Calculator - Калькулятор
• Finder - Файловый менеджер
• Safari - Браузер Safari
• ChromeApp - Google Chrome
• Terminal - Терминал
"""
    
    def _generate_with_ai(self, ai_context: Dict[str, Any]) -> GenerationResult:
        """
        Генерация макроса с помощью AI
        
        Args:
            ai_context: Контекст для AI
            
        Returns:
            Результат генерации
        """
        try:
            # TODO: Интеграция с реальным AI API (OpenAI, Gemini)
            # Пока используем заглушку для демонстрации
            
            user_input = ai_context["user_input"]
            intent = ai_context["intent_analysis"]
            
            # Простая эвристическая генерация для демонстрации
            mock_result = self._generate_mock_macro(user_input, intent)
            
            return GenerationResult(
                success=True,
                atlas_code=mock_result["atlas_code"],
                title=mock_result["title"],
                description=mock_result["description"],
                category=intent["category"],
                estimated_time=mock_result["estimated_time"],
                commands_count=mock_result["commands_count"],
                metadata=mock_result["metadata"]
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                atlas_code="",
                title="",
                description="",
                category="",
                estimated_time="",
                commands_count=0,
                metadata={},
                error=str(e)
            )
    
    def _generate_mock_macro(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация макроса-заглушки для демонстрации"""
        user_lower = user_input.lower()
        
        if "youtube" in user_lower and "python" in user_lower:
            return {
                "atlas_code": """# Поиск видео на YouTube
selenium_init url="https://www.youtube.com"
wait 3s
selenium_type selector="input#search" text="Python tutorials"
selenium_click selector="button#search-icon-legacy"
wait 5s""",
                "title": "Поиск Python видео на YouTube",
                "description": "Открывает YouTube и ищет видео по запросу Python",
                "estimated_time": "8-10 секунд",
                "commands_count": 5,
                "metadata": {
                    "platform": "macOS",
                    "requires_internet": True,
                    "complexity": "simple",
                    "automation_type": ["dom"]
                }
            }
        
        elif "калькулятор" in user_lower or "calculator" in user_lower:
            return {
                "atlas_code": """# Открытие калькулятора
open Calculator
wait 2s""",
                "title": "Открытие калькулятора",
                "description": "Запускает системное приложение Калькулятор",
                "estimated_time": "2-3 секунды",
                "commands_count": 2,
                "metadata": {
                    "platform": "macOS",
                    "requires_internet": False,
                    "complexity": "simple",
                    "automation_type": ["system"]
                }
            }
        
        else:
            return {
                "atlas_code": f"""# Автоматизация: {user_input}
# Сгенерированный макрос
open ChromeApp
wait 2s
# TODO: Добавить специфичные команды""",
                "title": f"Макрос: {user_input[:30]}",
                "description": f"Автоматизация для запроса: {user_input}",
                "estimated_time": "5-7 секунд",
                "commands_count": 3,
                "metadata": {
                    "platform": "macOS",
                    "requires_internet": False,
                    "complexity": intent.get("complexity", "simple"),
                    "automation_type": ["system"]
                }
            }
    
    def _validate_and_improve(self, result: GenerationResult) -> GenerationResult:
        """Валидация и улучшение сгенерированного макроса"""
        # TODO: Реализовать DSL валидацию
        # Пока просто возвращаем результат как есть
        self.logger.debug("🔍 DSL валидация пропущена (не реализована)")
        return result
    
    def _save_macro_to_file(self, result: GenerationResult, user_input: str):
        """Сохранение макроса в файл"""
        try:
            # Создаем директорию для макросов
            macros_dir = Path("data/generated_macros")
            macros_dir.mkdir(parents=True, exist_ok=True)
            
            # Генерируем имя файла
            safe_title = re.sub(r'[^\w\s-]', '', result.title).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.atlas"
            
            # Формируем полный контент файла
            full_content = f"""# Macro Atlas File
# Generated by Macro-Assistant
# Date: {datetime.now().isoformat()}
# Platform: macOS
# Description: {result.description}

# MACRO CODE
{result.atlas_code}

# METADATA
# Title: {result.title}
# Category: {result.category}
# Estimated Time: {result.estimated_time}
# Commands Count: {result.commands_count}
# User Input: {user_input}
# Generated: {datetime.now().isoformat()}
# Version: 1.0
"""
            
            # Сохраняем файл
            file_path = macros_dir / filename
            file_path.write_text(full_content, encoding='utf-8')
            
            self.logger.info(f"💾 Макрос сохранен: {file_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения макроса: {e}")
    
    def _get_cache_key(self, user_input: str, context: Optional[Dict[str, Any]]) -> str:
        """Генерация ключа кэша"""
        import hashlib
        text = user_input.lower().strip()
        context_str = json.dumps(context or {}, sort_keys=True)
        return hashlib.md5(f"{text}:{context_str}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[GenerationResult]:
        """Получение результата из кэша"""
        return self.generation_cache.get(cache_key)
    
    def _save_to_cache(self, cache_key: str, result: GenerationResult):
        """Сохранение результата в кэш"""
        self.generation_cache[cache_key] = result
        
        # Ограничиваем размер кэша
        if len(self.generation_cache) > 100:
            # Удаляем старые записи (простая стратегия)
            keys_to_remove = list(self.generation_cache.keys())[:20]
            for key in keys_to_remove:
                del self.generation_cache[key]
    
    def _format_response(self, result: GenerationResult, execution_time: float) -> Dict[str, Any]:
        """Форматирование ответа модуля"""
        return {
            "success": result.success,
            "result": result.atlas_code,
            "title": result.title,
            "description": result.description,
            "category": result.category,
            "estimated_time": result.estimated_time,
            "commands_count": result.commands_count,
            "execution_time": execution_time,
            "metadata": {
                **result.metadata,
                "module": "macro_generator",
                "generation_time": result.generation_time,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _format_error_response(self, error: str, execution_time: float) -> Dict[str, Any]:
        """Форматирование ответа об ошибке"""
        return {
            "success": False,
            "error": error,
            "execution_time": execution_time,
            "metadata": {
                "module": "macro_generator",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Информация о модуле"""
        return {
            "name": self.config["name"],
            "description": self.config["description"],
            "version": self.config["version"],
            "capabilities": self.config.get("capabilities", []),
            "supported_platforms": self.config.get("supported_platforms", []),
            "cache_size": len(self.generation_cache),
            "status": "ready"
        }

# Пример использования
if __name__ == "__main__":
    generator = MacroGenerator()
    
    test_requests = [
        "найди на YouTube видео про Python",
        "открой калькулятор",
        "поищи в Google информацию о нейронных сетях",
        "найди файлы PDF через Spotlight"
    ]
    
    print("🎭 Тестирование MacroGenerator")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        
        result = generator.handle(request, {"save_to_file": False})
        
        if result["success"]:
            print(f"   ✅ Успех: {result['title']}")
            print(f"   📝 Описание: {result['description']}")
            print(f"   ⏱️ Время выполнения: {result['estimated_time']}")
            print(f"   🔧 Команд: {result['commands_count']}")
            print(f"   📋 Код:")
            for line in result["result"].split('\n')[:3]:
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    print(f"\n📊 Информация о модуле:")
    info = generator.get_info()
    print(f"   Название: {info['name']}")
    print(f"   Версия: {info['version']}")
    print(f"   Кэш: {info['cache_size']} записей")
    print(f"   Статус: {info['status']}")
    
    print("\n🎭 MacroGenerator готов к работе!")
