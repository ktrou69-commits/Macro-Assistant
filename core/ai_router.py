#!/usr/bin/env python3
"""
🎯 AI Router для Macro-Assistant
Умный роутинг пользовательских запросов в соответствующие модули
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ModuleInfo:
    """Информация о модуле"""
    name: str
    description: str
    keywords: List[str]
    examples: List[str]
    confidence_threshold: float = 0.3
    load_time: str = "fast"  # fast, medium, slow

@dataclass
class RoutingResult:
    """Результат роутинга"""
    module: str
    confidence: float
    method: str  # fast_match, pattern_match, ai_analysis, fallback
    matched_keywords: List[str]
    execution_time: float
    metadata: Dict[str, Any]

class FastPatternMatcher:
    """Быстрый поиск по паттернам и ключевым словам"""
    
    def __init__(self):
        self.keyword_patterns = {}
        self.regex_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Компиляция паттернов для быстрого поиска"""
        
        # Паттерны для веб-автоматизации
        web_keywords = [
            r'\b(youtube|ютуб|ютьюб)\b',
            r'\b(google|гугл|гугле)\b',
            r'\b(twitter|твиттер)\b',
            r'\b(facebook|фейсбук)\b',
            r'\b(instagram|инстаграм)\b',
            r'\b(github|гитхаб)\b',
            r'\b(amazon|амазон)\b',
            r'\b(netflix|нетфликс)\b',
            r'\b(зайди на|перейди на|открой сайт)\b',
            r'\b(найди в интернете|поищи в сети)\b',
            r'\b(браузер|веб-страница|сайт)\b'
        ]
        
        # Паттерны для системной автоматизации
        system_keywords = [
            r'\b(калькулятор|calculator)\b',
            r'\b(finder|файндер)\b',
            r'\b(safari|сафари)\b',
            r'\b(настройки|preferences)\b',
            r'\b(открой приложение|запусти программу)\b',
            r'\b(системные команды|system)\b'
        ]
        
        # Паттерны для математических операций
        calculator_keywords = [
            r'\b(посчитай|вычисли|сколько будет)\b',
            r'[\d\s\+\-\*\/\=\(\)]+',
            r'\b(\d+\s*[\+\-\*\/]\s*\d+)\b',
            r'\b(процент|проценты|%)\b'
        ]
        
        # Паттерны для поиска файлов
        spotlight_keywords = [
            r'\b(найди файл|поищи документ)\b',
            r'\b(spotlight|спотлайт)\b',
            r'\b(на компьютере|в системе)\b',
            r'\b(pdf|doc|txt|jpg|png|mp3|mp4)\b',
            r'\b(документы|изображения|музыка|видео)\b'
        ]
        
        # Паттерны для создания структуры
        structure_keywords = [
            r'\b(структура|архитектура|интерфейс)\b',
            r'\b(создай структуру|построй архитектуру)\b',
            r'\b(элементы интерфейса|ui элементы)\b',
            r'\b(кнопки|поля|формы)\b'
        ]
        
        # Паттерны для переменных
        variable_keywords = [
            r'\b(переменная|переменные|variable)\b',
            r'\b(создай переменную|сохрани значение)\b',
            r'\b(параметр|параметры|настройка)\b'
        ]
        
        # Паттерны для селекторов
        selector_keywords = [
            r'\b(селектор|selector|css)\b',
            r'\b(dom элемент|веб элемент)\b',
            r'\b(xpath|css selector)\b',
            r'\b(найди элемент|извлеки селектор)\b'
        ]
        
        self.regex_patterns = {
            'macro_generator': web_keywords + system_keywords + calculator_keywords,
            'structure_builder': structure_keywords,
            'variable_creator': variable_keywords,
            'selector_creator': selector_keywords,
            'template_parser': [r'\b(шаблон|template|фото|изображение)\b']
        }
        
        # Компилируем регулярные выражения
        for module, patterns in self.regex_patterns.items():
            compiled_patterns = []
            for pattern in patterns:
                try:
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE | re.UNICODE))
                except re.error as e:
                    print(f"⚠️ Ошибка компиляции паттерна {pattern}: {e}")
            self.regex_patterns[module] = compiled_patterns
    
    def match(self, text: str) -> Dict[str, Tuple[float, List[str]]]:
        """
        Быстрый поиск совпадений
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь {модуль: (уверенность, совпавшие_паттерны)}
        """
        results = {}
        text_lower = text.lower()
        
        for module, patterns in self.regex_patterns.items():
            matches = []
            score = 0
            
            for pattern in patterns:
                if pattern.search(text_lower):
                    matches.append(pattern.pattern)
                    score += 1
            
            if matches:
                # Нормализуем счет
                confidence = min(score / 3.0, 1.0)  # Максимум при 3+ совпадениях
                results[module] = (confidence, matches)
        
        return results

class AIRouter:
    """
    Главный класс роутера для направления запросов в модули
    """
    
    def __init__(self):
        """Инициализация роутера"""
        self.modules: Dict[str, ModuleInfo] = {}
        self.fast_matcher = FastPatternMatcher()
        self.routing_cache = {}
        self.cache_ttl = 300  # 5 минут
        
        # Настройка логгера
        try:
            from .logger import get_logger
            self.logger = get_logger("ai_router")
        except ImportError:
            import logging
            self.logger = logging.getLogger("ai_router")
        
        # Загрузка информации о модулях
        self._load_modules_info()
        
        self.logger.info("🎯 AI Router инициализирован")
    
    def _load_modules_info(self):
        """Загрузка информации о доступных модулях"""
        try:
            from .config import get_config
            config = get_config()
            modules_dir = config.paths.modules
        except ImportError:
            modules_dir = Path("modules")
        
        if not modules_dir.exists():
            self.logger.warning(f"Директория модулей не найдена: {modules_dir}")
            return
        
        # Сканируем директории модулей
        for module_dir in modules_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('.'):
                continue
            
            config_file = module_dir / "config.json"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                module_info = ModuleInfo(
                    name=config_data.get("name", module_dir.name),
                    description=config_data.get("description", ""),
                    keywords=config_data.get("keywords", []),
                    examples=config_data.get("examples", []),
                    confidence_threshold=config_data.get("confidence_threshold", 0.3),
                    load_time=config_data.get("load_time", "fast")
                )
                
                self.modules[module_info.name] = module_info
                self.logger.debug(f"Загружен модуль: {module_info.name}")
                
            except Exception as e:
                self.logger.error(f"Ошибка загрузки модуля {module_dir.name}: {e}")
        
        self.logger.info(f"✅ Загружено {len(self.modules)} модулей")
    
    def route(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> RoutingResult:
        """
        Основной метод роутинга запроса
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            
        Returns:
            Результат роутинга
        """
        start_time = time.time()
        
        # Проверяем кэш
        cache_key = self._get_cache_key(user_input, context)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result.execution_time = time.time() - start_time
            self.logger.debug(f"Использован кэш для: {user_input[:50]}...")
            return cached_result
        
        self.logger.debug(f"🔍 Роутинг запроса: {user_input[:100]}...")
        
        # 1. Быстрый поиск по паттернам
        fast_result = self._fast_pattern_matching(user_input)
        if fast_result:
            result = RoutingResult(
                module=fast_result[0],
                confidence=fast_result[1],
                method="fast_match",
                matched_keywords=fast_result[2],
                execution_time=time.time() - start_time,
                metadata={"cache_used": False}
            )
            self._save_to_cache(cache_key, result)
            return result
        
        # 2. Поиск по ключевым словам модулей
        keyword_result = self._keyword_matching(user_input)
        if keyword_result:
            result = RoutingResult(
                module=keyword_result[0],
                confidence=keyword_result[1],
                method="keyword_match",
                matched_keywords=keyword_result[2],
                execution_time=time.time() - start_time,
                metadata={"cache_used": False}
            )
            self._save_to_cache(cache_key, result)
            return result
        
        # 3. AI анализ (если доступен)
        ai_result = self._ai_analysis(user_input, context)
        if ai_result:
            result = RoutingResult(
                module=ai_result[0],
                confidence=ai_result[1],
                method="ai_analysis",
                matched_keywords=ai_result[2],
                execution_time=time.time() - start_time,
                metadata={"cache_used": False, "ai_used": True}
            )
            self._save_to_cache(cache_key, result)
            return result
        
        # 4. Fallback на macro_generator
        result = RoutingResult(
            module="macro_generator",
            confidence=0.5,
            method="fallback",
            matched_keywords=[],
            execution_time=time.time() - start_time,
            metadata={"cache_used": False, "fallback": True}
        )
        
        self.logger.info(f"🎯 Роутинг завершен: {result.module} ({result.confidence:.2f}) за {result.execution_time:.3f}с")
        return result
    
    def _fast_pattern_matching(self, user_input: str) -> Optional[Tuple[str, float, List[str]]]:
        """Быстрый поиск по скомпилированным паттернам"""
        matches = self.fast_matcher.match(user_input)
        
        if not matches:
            return None
        
        # Находим лучшее совпадение
        best_module = max(matches.keys(), key=lambda m: matches[m][0])
        confidence, matched_patterns = matches[best_module]
        
        if confidence >= 0.6:  # Высокая уверенность
            self.logger.debug(f"Быстрое совпадение: {best_module} ({confidence:.2f})")
            return best_module, confidence, matched_patterns
        
        return None
    
    def _keyword_matching(self, user_input: str) -> Optional[Tuple[str, float, List[str]]]:
        """Поиск по ключевым словам модулей"""
        user_lower = user_input.lower()
        best_match = None
        best_score = 0
        best_keywords = []
        
        for module_name, module_info in self.modules.items():
            score = 0
            matched_keywords = []
            
            for keyword in module_info.keywords:
                if keyword.lower() in user_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Проверяем примеры
            for example in module_info.examples:
                if isinstance(example, dict) and "input" in example:
                    example_text = example["input"].lower()
                else:
                    example_text = str(example).lower()
                
                # Простая проверка схожести
                common_words = set(user_lower.split()) & set(example_text.split())
                if len(common_words) >= 2:
                    score += 2
                    matched_keywords.append(f"example_match: {example_text[:30]}...")
            
            if score > best_score:
                best_score = score
                best_match = module_name
                best_keywords = matched_keywords
        
        if best_match and best_score > 0:
            confidence = min(best_score / 3.0, 1.0)
            if confidence >= self.modules[best_match].confidence_threshold:
                self.logger.debug(f"Совпадение по ключевым словам: {best_match} ({confidence:.2f})")
                return best_match, confidence, best_keywords
        
        return None
    
    def _ai_analysis(self, user_input: str, context: Optional[Dict[str, Any]]) -> Optional[Tuple[str, float, List[str]]]:
        """AI анализ запроса (заглушка для будущей реализации)"""
        # TODO: Реализовать AI анализ через OpenAI API
        # Пока возвращаем None, чтобы использовался fallback
        
        try:
            # Здесь будет вызов AI модели для анализа намерений
            # Пример структуры промпта:
            prompt = f"""
            Проанализируй запрос пользователя и определи подходящий модуль.
            
            Доступные модули:
            {self._format_modules_for_ai()}
            
            Запрос: "{user_input}"
            
            Ответь в JSON формате:
            {{"module": "название_модуля", "confidence": 0.8, "reason": "объяснение"}}
            """
            
            # TODO: Вызов AI API
            # result = ai_client.generate(prompt)
            # return parse_ai_result(result)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка AI анализа: {e}")
            return None
    
    def _format_modules_for_ai(self) -> str:
        """Форматирование списка модулей для AI промпта"""
        modules_info = []
        for name, info in self.modules.items():
            modules_info.append(f"- {name}: {info.description}")
        return "\n".join(modules_info)
    
    def _get_cache_key(self, user_input: str, context: Optional[Dict[str, Any]]) -> str:
        """Генерация ключа кэша"""
        # Простой хэш от входных данных
        import hashlib
        text = user_input.lower().strip()
        context_str = json.dumps(context or {}, sort_keys=True)
        return hashlib.md5(f"{text}:{context_str}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[RoutingResult]:
        """Получение результата из кэша"""
        if cache_key not in self.routing_cache:
            return None
        
        cached_data, timestamp = self.routing_cache[cache_key]
        
        # Проверяем TTL
        if time.time() - timestamp > self.cache_ttl:
            del self.routing_cache[cache_key]
            return None
        
        return cached_data
    
    def _save_to_cache(self, cache_key: str, result: RoutingResult):
        """Сохранение результата в кэш"""
        self.routing_cache[cache_key] = (result, time.time())
        
        # Ограничиваем размер кэша
        if len(self.routing_cache) > 1000:
            # Удаляем старые записи
            oldest_keys = sorted(
                self.routing_cache.keys(),
                key=lambda k: self.routing_cache[k][1]
            )[:100]
            
            for key in oldest_keys:
                del self.routing_cache[key]
    
    def get_module_info(self, module_name: str) -> Optional[ModuleInfo]:
        """Получение информации о модуле"""
        return self.modules.get(module_name)
    
    def list_modules(self) -> List[str]:
        """Список доступных модулей"""
        return list(self.modules.keys())
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Статистика роутинга"""
        return {
            "loaded_modules": len(self.modules),
            "cache_entries": len(self.routing_cache),
            "cache_ttl": self.cache_ttl,
            "modules": {name: info.description for name, info in self.modules.items()}
        }
    
    def clear_cache(self):
        """Очистка кэша роутинга"""
        self.routing_cache.clear()
        self.logger.info("Кэш роутинга очищен")

# Глобальный экземпляр роутера
_router_instance: Optional[AIRouter] = None

def get_router() -> AIRouter:
    """Получение глобального экземпляра роутера"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AIRouter()
    return _router_instance

# Пример использования
if __name__ == "__main__":
    router = get_router()
    
    test_requests = [
        "найди на YouTube видео про Python",
        "открой калькулятор и посчитай 25 * 17",
        "создай переменную для хранения имени пользователя",
        "найди селектор для кнопки на сайте",
        "построй структуру интерфейса для приложения",
        "поищи файлы PDF на компьютере",
        "что-то совершенно неизвестное"
    ]
    
    print("🧪 Тестирование AI Router")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        result = router.route(request)
        
        print(f"   → Модуль: {result.module}")
        print(f"   → Уверенность: {result.confidence:.2f}")
        print(f"   → Метод: {result.method}")
        print(f"   → Время: {result.execution_time:.3f}с")
        if result.matched_keywords:
            print(f"   → Совпадения: {result.matched_keywords[:2]}")
    
    print(f"\n📊 Статистика:")
    stats = router.get_routing_stats()
    print(f"   Модулей загружено: {stats['loaded_modules']}")
    print(f"   Записей в кэше: {stats['cache_entries']}")
    
    print("\n🎯 AI Router готов к работе!")
